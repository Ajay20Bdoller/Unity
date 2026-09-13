import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.campaign import CampaignType


class CampaignCreate(BaseModel):
    key: str
    name: str
    campaign_type: CampaignType
    active: bool = True


class CampaignUpdate(BaseModel):
    name: str | None = None
    active: bool | None = None


class CampaignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    key: str
    name: str
    campaign_type: CampaignType
    active: bool
    created_at: datetime


class CampaignRegistrationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    school_id: uuid.UUID | None
    source: str | None
    created_at: datetime
