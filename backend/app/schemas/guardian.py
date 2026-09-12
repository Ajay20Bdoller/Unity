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
