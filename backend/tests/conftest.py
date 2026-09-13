import os

# Settings() requires these at import time. Tests that don't touch a real
# database only need config to load, not a live connection — set harmless
# defaults so `pytest` works out of the box with no .env file.
#
# DATABASE_URL points at a real local Postgres test database. Fast/unit
# tests never touch it (SQLAlchemy engine creation is lazy), and the
# `client` fixture below (used by live-DB integration tests) resets this
# exact database fresh at the start of the test session, then isolates
# each test in a rolled-back transaction — see below.
os.environ.setdefault(
    "DATABASE_URL", "postgresql://unity_test:unity_test@localhost:5432/unity_test"
)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")

import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

TEST_DB_NAME = "unity_test"
TEST_DB_USER = "unity_test"
TEST_DB_PASSWORD = "unity_test"
BACKEND_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _reset_rate_limiters():
    """The in-memory rate limiters (auth, AI) live for the whole process
    by design — correct in production, but this pytest run is one
    process for the *entire* suite, and TestClient requests all share
    one fake IP. Without this, whichever test runs late enough to be
    the 6th registration or 11th login attempt across the *whole run*
    starts failing on an unrelated 429, not the thing it's actually
    testing. Runs before every test; importing here (not at module
    level) avoids loading route modules for tests that never touch
    them."""
    from app.api.routes.ai import _rate_limiter as ai_limiter
    from app.api.routes.auth import (
        _forgot_password_limiter,
        _login_limiter,
        _register_limiter,
    )

    for limiter in (ai_limiter, _login_limiter, _register_limiter, _forgot_password_limiter):
        limiter.reset()
    yield


@pytest.fixture(scope="session")
def db_engine():
    """Resets the test database once per test run, then runs the real
    Alembic migrations against it (not Base.metadata.create_all) —
    several migrations seed rows the app depends on at request time
    (languages, career categories, the sample course/assessment), so a
    bare schema-only create would make plenty of real flows 500."""
    def run_as_postgres(sql: str, ignore_errors: bool = False) -> None:
        result = subprocess.run(
            ["su", "postgres", "-c", f'psql -v ON_ERROR_STOP=1 -c "{sql}"'],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 and not ignore_errors:
            raise RuntimeError(f"psql failed: {result.stderr}")

    run_as_postgres(
        f"CREATE USER {TEST_DB_USER} WITH PASSWORD '{TEST_DB_PASSWORD}' CREATEDB",
        ignore_errors=True,  # fine if it already exists from a previous run
    )
    run_as_postgres(
        f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
        f"WHERE datname = '{TEST_DB_NAME}' AND pid <> pg_backend_pid()"
    )
    run_as_postgres(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    run_as_postgres(f"CREATE DATABASE {TEST_DB_NAME} OWNER {TEST_DB_USER}")

    subprocess.run(
        ["python3", "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        env={**os.environ},
        check=True,
        capture_output=True,
    )

    engine = create_engine(os.environ["DATABASE_URL"])
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """One test = one outer transaction that always rolls back, so tests
    never see each other's data and never touch the seeded rows
    permanently — even though route code calls db.commit(), which would
    normally end the transaction. The SAVEPOINT-restart listener below
    is the standard pattern for that: every commit closes a nested
    SAVEPOINT, and this immediately opens a new one, while the real
    outer transaction (and its final rollback) is untouched."""
    connection = db_engine.connect()
    outer_transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:  # noqa: SLF001
            sess.begin_nested()

    yield session

    session.close()
    outer_transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """A TestClient wired to the isolated per-test session above instead
    of the app's normal engine — every request in a test hits the same
    rolled-back transaction."""
    from app.db.session import get_db
    from app.main import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)


def _register_and_login(client, payload):
    reg = client.post("/auth/register", json=payload)
    assert reg.status_code == 201, reg.text
    identifier = payload.get("email") or payload.get("mobile_number")
    login = client.post("/auth/login", json={"identifier": identifier, "password": payload["password"]})
    assert login.status_code == 200, login.text
    return reg.json()


def _independent_client(db_session):
    """A fresh TestClient with its own cookie jar. Depending on `client`
    (rather than `db_session` directly) as well would be redundant — the
    override it installs lives on the shared `app` object, not on any
    particular TestClient instance, so every TestClient(app) create here
    already sees the same isolated session. The role fixtures below
    depend on `client` anyway, only to guarantee ordering: the override
    must be installed before any of them registers a user."""
    from app.main import app

    return TestClient(app)


@pytest.fixture()
def student_client(client, db_session):
    """Its own TestClient/cookie-jar — independent from `client` and
    every other *_client fixture, so using several of these together in
    one test doesn't have one login silently clobber another's cookies
    (that was a real bug here: every *_client fixture originally reused
    the single shared `client`, so whichever fixture logged in *last*
    won every other fixture's session too)."""
    independent = _independent_client(db_session)
    _register_and_login(
        independent,
        {
            "full_name": "Role Matrix Student",
            "role": "student",
            "mobile_number": "9100000001",
            "password": "TestPass123!",
            "date_of_birth": "2010-01-01",
            "school_name": "School",
            "parent_name": "Parent",
            "parent_relation": "Mother",
            "address": "addr",
            "district": "d",
            "state": "s",
        },
    )
    return independent


@pytest.fixture()
def parent_client(client, db_session):
    independent = _independent_client(db_session)
    _register_and_login(
        independent,
        {
            "full_name": "Role Matrix Parent",
            "role": "parent",
            "email": "rolematrix-parent@example.com",
            "mobile_number": "9100000002",
            "password": "TestPass123!",
            "student_name": "Someone",
            "relation_to_student": "Mother",
        },
    )
    return independent


@pytest.fixture()
def mentor_client(client, db_session):
    independent = _independent_client(db_session)
    _register_and_login(
        independent,
        {
            "full_name": "Role Matrix Mentor",
            "role": "mentor",
            "email": "rolematrix-mentor@example.com",
            "mobile_number": "9100000003",
            "password": "TestPass123!",
            "date_of_birth": "1990-01-01",
        },
    )
    return independent


@pytest.fixture()
def school_admin_client(client, db_session):
    independent = _independent_client(db_session)
    _register_and_login(
        independent,
        {
            "full_name": "Role Matrix School Admin",
            "role": "school_admin",
            "email": "rolematrix-school@example.com",
            "mobile_number": "9100000004",
            "password": "TestPass123!",
            "date_of_birth": "1980-01-01",
            "school_name": "School",
            "school_location": "Location",
        },
    )
    return independent


@pytest.fixture()
def admin_client(client, db_session):
    """Admin accounts can't self-register, so this inserts one directly
    via the same isolated session every fixture here shares, matching
    what scripts/create_admin.py does in real usage."""
    from app.core.security import hash_password
    from app.models.user import User, UserRole

    user = User(
        email="rolematrix-admin@example.com",
        full_name="Role Matrix Admin",
        role=UserRole.ADMIN,
        hashed_password=hash_password("TestPass123!"),
    )
    db_session.add(user)
    db_session.commit()

    independent = _independent_client(db_session)
    login = independent.post(
        "/auth/login",
        json={"identifier": "rolematrix-admin@example.com", "password": "TestPass123!"},
    )
    assert login.status_code == 200, login.text
    return independent
