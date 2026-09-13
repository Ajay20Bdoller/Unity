import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class PublishStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Announcement(Base):
    """`audience` is a list of role values; empty/null means visible to
    every role. One row per language — there's no translation table
    here (unlike careers/courses); an announcement in Hindi and its
    English counterpart are two separate rows, and the route falls back
    to English if nothing exists in the reader's language."""

    __tablename__ = "announcements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    audience: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    language_code: Mapped[str] = mapped_column(
        String(10), ForeignKey("languages.code"), nullable=False, default="en"
    )
    publish_status: Mapped[PublishStatus] = mapped_column(
        Enum(PublishStatus, name="publish_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=PublishStatus.DRAFT,
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
