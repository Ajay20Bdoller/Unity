import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.announcement import PublishStatus


class AnnouncementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    content: str
    language_code: str
    published_at: datetime | None


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    audience: list[str] | None = None
    language_code: str = "en"


class AnnouncementUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    audience: list[str] | None = None


class AnnouncementAdminRead(AnnouncementRead):
    audience: list[str] | None
    publish_status: PublishStatus
