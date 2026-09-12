import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class StudentProfileUpdate(BaseModel):
    date_of_birth: date | None = None
    class_level: str | None = None
    school_id: uuid.UUID | None = None
    state_id: uuid.UUID | None = None
    district_id: uuid.UUID | None = None
    gender: str | None = None
    mobile_number: str | None = None
    profile_photo_url: str | None = None


class StudentProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    date_of_birth: date | None
    class_level: str | None
    school_id: uuid.UUID | None
    state_id: uuid.UUID | None
    district_id: uuid.UUID | None
    gender: str | None
    mobile_number: str | None
    profile_photo_url: str | None
    created_at: datetime
    updated_at: datetime
