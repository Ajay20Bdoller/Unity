import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_parent
from app.core.config import get_settings
from app.core.consent import generate_otp, hash_otp, otp_expiry
from app.db.session import get_db
from app.models.consent import ConsentRecord, ConsentStatus, ConsentType
from app.models.guardian import GuardianRelationship, GuardianRelationshipStatus
from app.models.user import User
from app.schemas.consent import ConsentOTPResponse, ConsentOTPVerifyRequest, ConsentRecordRead
from app.schemas.guardian import GuardianRelationshipRead

router = APIRouter(prefix="/parents", tags=["parents"])
settings = get_settings()


def _get_owned_relationship(db: Session, current_user: User, relationship_id) -> GuardianRelationship:
    relationship = db.get(GuardianRelationship, relationship_id)
    if not relationship or relationship.parent_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
    return relationship


@router.get("/me/guardians", response_model=list[GuardianRelationshipRead])
def list_my_guardian_relationships(
    current_user: User = Depends(require_parent), db: Session = Depends(get_db)
) -> list[GuardianRelationshipRead]:
    rows = (
        db.query(GuardianRelationship, User)
        .join(User, User.id == GuardianRelationship.student_id)
        .filter(GuardianRelationship.parent_id == current_user.id)
        .order_by(GuardianRelationship.created_at.desc())
        .all()
    )
    return [
        GuardianRelationshipRead(
            id=rel.id,
            student_id=rel.student_id,
            parent_id=rel.parent_id,
            status=rel.status,
            created_at=rel.created_at,
            verified_at=rel.verified_at,
            student_name=student.full_name,
            student_email=student.email,
        )
        for rel, student in rows
    ]


@router.post("/me/guardians/{relationship_id}/verify", response_model=GuardianRelationshipRead)
def verify_guardian_relationship(
    relationship_id: uuid.UUID,
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
) -> GuardianRelationship:
    relationship = _get_owned_relationship(db, current_user, relationship_id)
    if relationship.status != GuardianRelationshipStatus.PENDING:
        raise HTTPException(status_code=400, detail="Relationship is not pending")

    relationship.status = GuardianRelationshipStatus.VERIFIED
    relationship.verified_at = datetime.now(timezone.utc)
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    return relationship


@router.post("/me/guardians/{relationship_id}/reject", response_model=GuardianRelationshipRead)
def reject_guardian_relationship(
    relationship_id: uuid.UUID,
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
) -> GuardianRelationship:
    relationship = _get_owned_relationship(db, current_user, relationship_id)
    if relationship.status != GuardianRelationshipStatus.PENDING:
        raise HTTPException(status_code=400, detail="Relationship is not pending")

    relationship.status = GuardianRelationshipStatus.REJECTED
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    return relationship


def _get_or_create_consent_record(
    db: Session, relationship_id, consent_type: ConsentType
) -> ConsentRecord:
    record = (
        db.query(ConsentRecord)
        .filter(
            ConsentRecord.guardian_relationship_id == relationship_id,
            ConsentRecord.consent_type == consent_type,
        )
        .first()
    )
    if not record:
        record = ConsentRecord(
            guardian_relationship_id=relationship_id,
            consent_type=consent_type,
            status=ConsentStatus.PENDING,
        )
        db.add(record)
        db.flush()
    return record


@router.post(
    "/me/guardians/{relationship_id}/consent/{consent_type}/request-otp",
    response_model=ConsentOTPResponse,
)
def request_consent_otp(
    relationship_id: uuid.UUID,
    consent_type: ConsentType,
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
) -> ConsentOTPResponse:
    relationship = _get_owned_relationship(db, current_user, relationship_id)
    if relationship.status != GuardianRelationshipStatus.VERIFIED:
        raise HTTPException(
            status_code=400, detail="Guardian relationship must be verified before requesting consent"
        )

    record = _get_or_create_consent_record(db, relationship.id, consent_type)
    if record.status == ConsentStatus.GRANTED:
        raise HTTPException(status_code=409, detail="Consent already granted")

    raw_otp = generate_otp()
    record.otp_hash = hash_otp(raw_otp)
    record.otp_expires_at = otp_expiry()
    record.otp_attempts = 0
    record.status = ConsentStatus.PENDING
    db.add(record)
    db.commit()

    # No real SMS provider wired up yet (see CLAUDE.md) — whether the
    # OTP is echoed back here is controlled by expose_dev_otp, which is
    # NOT the same thing as ENVIRONMENT=production: a pilot deployment
    # needs production's secure-cookie behavior but may still need this
    # on until SMS exists. See app/core/config.py.
    is_dev = settings.expose_dev_otp
    return ConsentOTPResponse(
        message="OTP generated." if is_dev else "OTP sent.",
        dev_otp=raw_otp if is_dev else None,
    )


@router.post(
    "/me/guardians/{relationship_id}/consent/{consent_type}/verify-otp",
    response_model=ConsentRecordRead,
)
def verify_consent_otp(
    relationship_id: uuid.UUID,
    consent_type: ConsentType,
    payload: ConsentOTPVerifyRequest,
    current_user: User = Depends(require_parent),
    db: Session = Depends(get_db),
) -> ConsentRecord:
    relationship = _get_owned_relationship(db, current_user, relationship_id)
    record = (
        db.query(ConsentRecord)
        .filter(
            ConsentRecord.guardian_relationship_id == relationship.id,
            ConsentRecord.consent_type == consent_type,
        )
        .first()
    )
    invalid = HTTPException(status_code=400, detail="Invalid or expired OTP")
    if not record or not record.otp_hash or not record.otp_expires_at:
        raise invalid
    if record.otp_attempts >= settings.OTP_MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many attempts — request a new OTP")
    if record.otp_expires_at < datetime.now(timezone.utc):
        raise invalid

    if hash_otp(payload.otp) != record.otp_hash:
        record.otp_attempts += 1
        db.add(record)
        db.commit()
        raise invalid

    record.status = ConsentStatus.GRANTED
    record.verified_at = datetime.now(timezone.utc)
    record.verification_method = "otp_dev_mode" if settings.expose_dev_otp else "otp"
    record.otp_hash = None
    record.otp_expires_at = None
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
