import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class StudentProfileUpdate(BaseModel):
    date_of_birth: date | None = None
    class_level: str | None = None
    school_id: uuid.UUID | None = None
    school_name: str | None = None
    state_id: uuid.UUID | None = None
    district_id: uuid.UUID | None = None
    address: str | None = None
    district: str | None = None
    state: str | None = None
    country: str | None = None
    parent_name: str | None = None
    parent_relation: str | None = None
    gender: str | None = None
    profile_photo_url: str | None = None


class StudentProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    date_of_birth: date | None
    class_level: str | None
    school_id: uuid.UUID | None
    school_name: str | None
    state_id: uuid.UUID | None
    district_id: uuid.UUID | None
    address: str | None
    district: str | None
    state: str | None
    country: str | None
    parent_name: str | None
    parent_relation: str | None
    gender: str | None
    profile_photo_url: str | None
    created_at: datetime
    updated_at: datetime
