import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate

STUDENT_FULL = dict(
    full_name="S",
    role="student",
    password="TestPass123!",
    mobile_number="9000000000",
    date_of_birth="2010-01-01",
    school_name="X School",
    parent_name="P",
    parent_relation="Mother",
    address="addr",
    district="d",
    state="s",
)


def test_student_requires_email_or_mobile():
    payload = {**STUDENT_FULL}
    payload.pop("mobile_number")
    with pytest.raises(ValidationError):
        UserCreate(**payload)


def test_student_accepts_mobile_only_no_email():
    user = UserCreate(**STUDENT_FULL)
    assert user.email is None
    assert user.mobile_number == "9000000000"


def test_student_missing_school_name_rejected():
    payload = {**STUDENT_FULL}
    payload.pop("school_name")
    with pytest.raises(ValidationError):
        UserCreate(**payload)


def test_parent_requires_email_and_student_info():
    with pytest.raises(ValidationError):
        UserCreate(
            full_name="P", role="parent", password="TestPass123!", mobile_number="9000000001"
        )
    user = UserCreate(
        full_name="P",
        role="parent",
        password="TestPass123!",
        email="p@example.com",
        mobile_number="9000000001",
        student_name="S",
        relation_to_student="Mother",
    )
    assert user.email == "p@example.com"


def test_mentor_requires_dob():
    with pytest.raises(ValidationError):
        UserCreate(
            full_name="M",
            role="mentor",
            password="TestPass123!",
            email="m@example.com",
            mobile_number="9000000002",
        )
    user = UserCreate(
        full_name="M",
        role="mentor",
        password="TestPass123!",
        email="m@example.com",
        mobile_number="9000000002",
        date_of_birth="1990-01-01",
    )
    assert user.date_of_birth is not None


def test_school_admin_requires_school_fields():
    with pytest.raises(ValidationError):
        UserCreate(
            full_name="A",
            role="school_admin",
            password="TestPass123!",
            email="a@example.com",
            mobile_number="9000000003",
            date_of_birth="1980-01-01",
        )
    user = UserCreate(
        full_name="A",
        role="school_admin",
        password="TestPass123!",
        email="a@example.com",
        mobile_number="9000000003",
        date_of_birth="1980-01-01",
        school_name="Some School",
        school_location="Somewhere",
    )
    assert user.school_name == "Some School"
