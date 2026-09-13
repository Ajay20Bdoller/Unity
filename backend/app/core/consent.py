import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.consent import ConsentRecord, ConsentStatus, ConsentType

settings = get_settings()


def generate_otp() -> str:
    """6-digit numeric OTP. Dev-mode delivery only (see app/api/routes/
    parents.py — the OTP is echoed in the API response when
    ENVIRONMENT=development instead of being sent by SMS). Wiring a real
    SMS provider is a prerequisite for production; not built here."""
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(raw_otp: str) -> str:
    return hashlib.sha256(raw_otp.encode("utf-8")).hexdigest()


def otp_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)


def has_active_consent(
    db: Session, guardian_relationship_id: uuid.UUID, consent_type: ConsentType
) -> bool:
    """The one function any sensitive feature (mentorship, data sharing,
    ...) should call before proceeding. Missing, pending, rejected,
    revoked, and expired consent all just mean "not allowed" — callers
    don't need to know which, they only need a yes/no.
    """
    record = (
        db.query(ConsentRecord)
        .filter(
            ConsentRecord.guardian_relationship_id == guardian_relationship_id,
            ConsentRecord.consent_type == consent_type,
        )
        .first()
    )
    if not record or record.status != ConsentStatus.GRANTED:
        return False
    if record.expires_at is not None and record.expires_at < datetime.now(timezone.utc):
        return False
    return True


def student_has_any_active_consent(db: Session, student_id: uuid.UUID, consent_type: ConsentType) -> bool:
    """Convenience for routes that only know the student, not a specific
    guardian relationship: true if ANY of the student's guardian
    relationships has active consent for this type."""
    from app.models.guardian import GuardianRelationship

    relationship_ids = [
        r[0]
        for r in db.query(GuardianRelationship.id)
        .filter(GuardianRelationship.student_id == student_id)
        .all()
    ]
    return any(has_active_consent(db, rid, consent_type) for rid in relationship_ids)
