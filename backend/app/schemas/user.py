import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator

from app.models.user import UserRole


class UserBase(BaseModel):
    full_name: str
    role: UserRole = UserRole.STUDENT
    preferred_language: str = "en"
    email: EmailStr | None = None
    mobile_number: str | None = None


class UserCreate(UserBase):
    password: str
    campaign_key: str | None = None
    source: str | None = None

    # Student-only (email optional for students; the rest fill in a
    # profile the current onboarding endpoints don't ask for again).
    date_of_birth: date | None = None
    school_name: str | None = None
    parent_name: str | None = None
    parent_relation: str | None = None
    address: str | None = None
    district: str | None = None
    state: str | None = None
    country: str | None = "India"

    # Parent-only (informational — see ParentProfile docstring)
    student_name: str | None = None
    relation_to_student: str | None = None

    # School admin-only
    school_location: str | None = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value

    @model_validator(mode="after")
    def role_specific_requirements(self) -> "UserCreate":
        missing: list[str] = []

        if self.role == UserRole.STUDENT:
            if not self.email and not self.mobile_number:
                missing.append("email or mobile_number")
            if not self.date_of_birth:
                missing.append("date_of_birth")
            if not self.school_name:
                missing.append("school_name")
            if not self.mobile_number:
                missing.append("mobile_number")
            if not self.parent_name:
                missing.append("parent_name")
            if not self.parent_relation:
                missing.append("parent_relation")
            if not self.address:
                missing.append("address")
            if not self.district:
                missing.append("district")
            if not self.state:
                missing.append("state")
        elif self.role == UserRole.PARENT:
            if not self.email:
                missing.append("email")
            if not self.mobile_number:
                missing.append("mobile_number")
            if not self.student_name:
                missing.append("student_name")
            if not self.relation_to_student:
                missing.append("relation_to_student")
        elif self.role == UserRole.MENTOR:
            if not self.email:
                missing.append("email")
            if not self.date_of_birth:
                missing.append("date_of_birth")
            if not self.mobile_number:
                missing.append("mobile_number")
        elif self.role == UserRole.SCHOOL_ADMIN:
            if not self.email:
                missing.append("email")
            if not self.date_of_birth:
                missing.append("date_of_birth")
            if not self.mobile_number:
                missing.append("mobile_number")
            if not self.school_name:
                missing.append("school_name")
            if not self.school_location:
                missing.append("school_location")

        if missing:
            raise ValueError(f"Missing required fields for {self.role.value}: {', '.join(missing)}")
        return self


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime


class LanguageUpdate(BaseModel):
    preferred_language: str
