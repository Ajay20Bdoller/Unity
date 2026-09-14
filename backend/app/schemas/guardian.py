import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.guardian import GuardianRelationshipStatus


class GuardianInviteRequest(BaseModel):
    parent_email: EmailStr


class GuardianRelationshipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    parent_id: uuid.UUID
    status: GuardianRelationshipStatus
    created_at: datetime
    verified_at: datetime | None
    # populated for the parent-facing endpoints (which student this is)
    student_name: str | None = None
    student_email: str | None = None
    # populated for the student-facing endpoints (which parent this is)
    parent_name: str | None = None
    parent_email: str | None = None
