import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class MentorshipRequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"


class MentorExpertise(Base):
    __tablename__ = "mentor_expertise"
    __table_args__ = (
        UniqueConstraint("mentor_id", "career_category_id", name="uq_mentor_expertise"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mentor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    career_category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("career_categories.id"), nullable=False
    )


class MentorLanguage(Base):
    __tablename__ = "mentor_languages"
    __table_args__ = (UniqueConstraint("mentor_id", "language_code", name="uq_mentor_language"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mentor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    language_code: Mapped[str] = mapped_column(
        String(10), ForeignKey("languages.code"), nullable=False
    )


class MentorshipRequest(Base):
    """Gated on consent, not just identity: a student may only create one
    of these if they have an active (GRANTED, unexpired) MENTORSHIP
    consent record under some guardian relationship — see
    app.core.consent.has_active_consent, checked in the route, not here.
    'Manual/admin matching' for now: mentor accepts/declines directly,
    no automated matching algorithm."""

    __tablename__ = "mentorship_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    mentor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[MentorshipRequestStatus] = mapped_column(
        Enum(
            MentorshipRequestStatus,
            name="mentorship_request_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=MentorshipRequestStatus.PENDING,
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MentorshipSession(Base):
    """A record that a mentorship interaction happened/is planned — not
    a live chat or video system. `notes` is a plain summary, not a
    message log; this is deliberately not a messaging feature."""

    __tablename__ = "mentorship_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mentorship_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mentorship_requests.id"), nullable=False, index=True
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MentorshipFeedback(Base):
    __tablename__ = "mentorship_feedback"
    __table_args__ = (
        UniqueConstraint("session_id", "given_by_user_id", name="uq_mentorship_feedback"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mentorship_sessions.id"), nullable=False, index=True
    )
    given_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
