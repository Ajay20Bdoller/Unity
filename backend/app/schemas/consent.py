import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.consent import ConsentStatus, ConsentType


class ConsentOTPResponse(BaseModel):
    message: str
    dev_otp: str | None = None  # only populated when ENVIRONMENT=development


class ConsentOTPVerifyRequest(BaseModel):
    otp: str


class ConsentRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    guardian_relationship_id: uuid.UUID
    consent_type: ConsentType
    status: ConsentStatus
    requested_at: datetime
    verified_at: datetime | None
    expires_at: datetime | None
