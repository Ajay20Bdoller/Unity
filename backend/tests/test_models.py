from app.models.user import User, UserRole


def test_role_column_uses_lowercase_enum_values():
    """Regression test.

    Without values_callable, SQLAlchemy sends the Python enum member's
    .name ("STUDENT") to Postgres instead of .value ("student"), which
    doesn't match the values the Alembic migration creates and makes
    every insert fail. This checks the column metadata directly, no DB
    needed.
    """
    role_type = User.__table__.c.role.type
    assert set(role_type.enums) == {r.value for r in UserRole}
