import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.consent import ConsentStatus, ConsentType
from app.models.guardian import GuardianRelationshipStatus


class AdminConsentSummary(BaseModel):
    consent_type: ConsentType
    status: ConsentStatus


class AdminGuardianRelationshipRead(BaseModel):
    id: uuid.UUID
    student_name: str
    parent_name: str
    parent_contact: str | None
    status: GuardianRelationshipStatus
    created_at: datetime
    verified_at: datetime | None
    consents: list[AdminConsentSummary]
