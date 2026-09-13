import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CampaignType(str, enum.Enum):
    SCHOOL = "school"
    COACHING = "coaching"
    COMMUNITY = "community"
    ONLINE = "online"
    REFERRAL = "referral"


class Campaign(Base):
    """Purely an internal acquisition-tracking tool — nothing else in
    the product depends on this existing. `key` is the short code a
    student would enter (or land via a link) at registration time."""

    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    campaign_type: Mapped[CampaignType] = mapped_column(
        Enum(CampaignType, name="campaign_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CampaignRegistration(Base):
    """One row per user who registered while a campaign key was present.
    A bad/unknown campaign_key at registration is silently ignored (see
    the register route) — tracking failure must never block someone
    from creating an account."""

    __tablename__ = "campaign_registrations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False, index=True
    )
    school_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schools.id"), nullable=True
    )
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
