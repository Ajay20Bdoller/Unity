"""These tests use the `client` fixture (see conftest.py), which runs
against a real, freshly-migrated Postgres database with each test
isolated in a rolled-back transaction. Unlike the rest of the suite,
these actually exercise routes end-to-end through the DB — this is
the automated version of the manual curl verification every feature
in this repo was originally checked with.
"""

STUDENT_PAYLOAD = {
    "full_name": "Integration Student",
    "role": "student",
    "mobile_number": "9000010001",
    "password": "TestPass123!",
    "date_of_birth": "2010-01-01",
    "school_name": "Test School",
    "parent_name": "Test Parent",
    "parent_relation": "Mother",
    "address": "Test address",
    "district": "Test district",
    "state": "Test state",
}


def register(client, **overrides):
    payload = {**STUDENT_PAYLOAD, **overrides}
    return client.post("/auth/register", json=payload)


def test_register_and_login_with_mobile_only(client):
    res = register(client)
    assert res.status_code == 201
    body = res.json()
    assert body["email"] is None
    assert body["mobile_number"] == "9000010001"

    login = client.post(
        "/auth/login", json={"identifier": "9000010001", "password": "TestPass123!"}
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_full_auth_lifecycle(client):
    register(client, mobile_number="9000010002")
    login = client.post(
        "/auth/login", json={"identifier": "9000010002", "password": "TestPass123!"}
    )
    assert login.status_code == 200

    me = client.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["full_name"] == "Integration Student"

    refresh = client.post("/auth/refresh")
    assert refresh.status_code == 200

    logout = client.post("/auth/logout")
    assert logout.status_code == 204

    refresh_after_logout = client.post("/auth/refresh")
    assert refresh_after_logout.status_code == 401

    me_after_logout = client.get("/auth/me")
    assert me_after_logout.status_code == 401


def test_admin_cannot_self_register(client):
    res = client.post(
        "/auth/register",
        json={
            "full_name": "Sneaky Admin",
            "role": "admin",
            "email": "sneaky@example.com",
            "password": "TestPass123!",
        },
    )
    assert res.status_code == 400


def test_duplicate_mobile_number_rejected(client):
    register(client, mobile_number="9000010003")
    dup = register(client, mobile_number="9000010003", full_name="Someone Else")
    assert dup.status_code == 400


def test_wrong_password_rejected(client):
    register(client, mobile_number="9000010004")
    res = client.post(
        "/auth/login", json={"identifier": "9000010004", "password": "WrongPassword1!"}
    )
    assert res.status_code == 401
