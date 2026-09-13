import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    PARENT = "parent"
    MENTOR = "mentor"
    SCHOOL_ADMIN = "school_admin"
    ADMIN = "admin"


# Roles a person can pick for themselves at /auth/register. ADMIN is
# deliberately excluded — admin accounts are provisioned separately
# (seed script / an existing admin), never via open self-registration.
SELF_REGISTERABLE_ROLES = (
    UserRole.STUDENT,
    UserRole.PARENT,
    UserRole.MENTOR,
    UserRole.SCHOOL_ADMIN,
)


class User(Base):
    """Identity/auth only. `email` and `mobile_number` are both optional
    individually but at least one must be present — a student who is a
    minor without an email account can register and log in with just a
    mobile number instead (see the CHECK constraint below and the
    login route, which accepts either as the identifier)."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "email IS NOT NULL OR mobile_number IS NOT NULL",
            name="ck_users_email_or_mobile",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    mobile_number: Mapped[str | None] = mapped_column(
        String(20), unique=True, index=True, nullable=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserRole.STUDENT,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    preferred_language: Mapped[str] = mapped_column(
        String(10), ForeignKey("languages.code"), default="en", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
