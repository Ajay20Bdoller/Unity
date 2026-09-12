import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ConsentType(str, enum.Enum):
    MENTORSHIP = "mentorship"
    DATA_SHARING = "data_sharing"


class ConsentStatus(str, enum.Enum):
    PENDING = "pending"
    GRANTED = "granted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ConsentRecord(Base):
    """One row per (guardian_relationship, consent_type). Sensitive
    features must check this directly (see app/core/consent.py) rather
    than inferring permission from the guardian relationship being
    VERIFIED — identity verification and feature consent are deliberately
    separate axes (§6).

    OTP is dev-mode only: no SMS provider is wired up (see
    app/core/consent.py generate_otp / ENVIRONMENT check). A real
    provider is a prerequisite for production, not built here.
    """

    __tablename__ = "consent_records"
    __table_args__ = (
        UniqueConstraint(
            "guardian_relationship_id", "consent_type", name="uq_consent_relationship_type"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    guardian_relationship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("guardian_relationships.id"), nullable=False, index=True
    )
    consent_type: Mapped[ConsentType] = mapped_column(
        Enum(ConsentType, name="consent_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    status: Mapped[ConsentStatus] = mapped_column(
        Enum(ConsentStatus, name="consent_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ConsentStatus.PENDING,
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_method: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # OTP verification state — never store the raw OTP, only its hash.
    otp_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    otp_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    otp_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
