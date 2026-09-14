import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.consent import ConsentRecord, ConsentStatus, ConsentType
from app.models.guardian import GuardianRelationship, GuardianRelationshipStatus
from app.models.user import User
from app.schemas.admin_consent import AdminConsentSummary, AdminGuardianRelationshipRead

router = APIRouter(prefix="/admin/guardian-relationships", tags=["admin"])


def _serialize(db: Session, rel: GuardianRelationship) -> AdminGuardianRelationshipRead:
    student = db.get(User, rel.student_id)
    parent = db.get(User, rel.parent_id)
    consents = (
        db.query(ConsentRecord).filter(ConsentRecord.guardian_relationship_id == rel.id).all()
    )
    return AdminGuardianRelationshipRead(
        id=rel.id,
        student_name=student.full_name if student else "Unknown",
        parent_name=parent.full_name if parent else "Unknown",
        parent_contact=(parent.email or parent.mobile_number) if parent else None,
        status=rel.status,
        created_at=rel.created_at,
        verified_at=rel.verified_at,
        consents=[
            AdminConsentSummary(consent_type=c.consent_type, status=c.status)
            for c in consents
        ],
    )


@router.get("", response_model=list[AdminGuardianRelationshipRead])
def list_guardian_relationships(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
) -> list[AdminGuardianRelationshipRead]:
    rels = db.query(GuardianRelationship).order_by(GuardianRelationship.created_at.desc()).all()
    return [_serialize(db, r) for r in rels]


@router.post(
    "/{relationship_id}/consent/{consent_type}/grant",
    response_model=AdminGuardianRelationshipRead,
)
def admin_grant_consent(
    relationship_id: uuid.UUID,
    consent_type: ConsentType,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminGuardianRelationshipRead:
    """Grants a specific consent without the OTP flow — for a pilot with
    no real SMS provider yet (see CLAUDE.md), where the admin has
    personally verified the parent's agreement some other way (a phone
    call, in person, etc.) rather than relaying an OTP by hand.

    Still requires the guardian_relationship itself to be VERIFIED —
    that's the parent's own account confirming the link, which this
    endpoint does not shortcut. Only the consent-OTP step is skipped.
    """
    rel = db.get(GuardianRelationship, relationship_id)
    if not rel:
        raise HTTPException(status_code=404, detail="Guardian relationship not found")
    if rel.status != GuardianRelationshipStatus.VERIFIED:
        raise HTTPException(
            status_code=400,
            detail="The guardian relationship itself must be verified (by the parent's own "
            "account) before consent can be granted for it.",
        )

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
            guardian_relationship_id=relationship_id, consent_type=consent_type
        )
    record.status = ConsentStatus.GRANTED
    record.verified_at = datetime.now(timezone.utc)
    record.verification_method = "admin_override"
    record.otp_hash = None
    record.otp_expires_at = None
    db.add(record)
    db.commit()

    return _serialize(db, rel)
