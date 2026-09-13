import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class StudentProfile(Base):
    """Student-only fields. 1:1 with users — never merge these into User.

    school_id/state_id/district_id (FK, structured) are reserved for
    once real location/school directories are seeded (see CLAUDE.md
    gaps) — until then, school_name/district/state/country are the
    free-text fields registration actually collects and display. Both
    sets are kept rather than removing the FK columns, so a future
    migration can backfill structured references without a schema
    change; nothing currently reads the FK columns.

    parent_name/parent_relation are informational only — they do NOT
    create a guardian_relationship by themselves. That's a separate,
    verified flow (see app/models/guardian.py); this is just what the
    student told us at registration, which may predate or duplicate it.
    """

    __tablename__ = "students"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    class_level: Mapped[str | None] = mapped_column(String(20), nullable=True)  # "10", "12", ...
    school_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schools.id"), nullable=True
    )
    school_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("states.id"), nullable=True
    )
    district_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("districts.id"), nullable=True
    )
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True, default="India")
    parent_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_relation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    profile_photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ParentProfile(Base):
    """student_name/relation_to_student are informational (what the
    parent told us), same caveat as StudentProfile.parent_name above —
    the verified link is guardian_relationship, not this."""

    __tablename__ = "parents"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    student_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    relation_to_student: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MentorProfile(Base):
    __tablename__ = "mentors"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    availability_note: Mapped[str | None] = mapped_column(String(300), nullable=True)
    # A mentor is invisible to students (not returned by GET /mentors,
    # and can't receive requests even by direct API call — see
    # mentorship.py) until an admin approves them. Registering does not
    # imply any vetting has happened.
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SchoolAdminProfile(Base):
    __tablename__ = "school_admin_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    school_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schools.id"), nullable=True
    )
    school_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    school_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
