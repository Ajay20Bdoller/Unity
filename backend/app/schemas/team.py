import uuid

from pydantic import BaseModel, ConfigDict


class TeamMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    role_title: str
    bio: str | None
    photo_url: str | None
    linkedin_url: str | None
    display_order: int


class TeamMemberCreate(BaseModel):
    full_name: str
    role_title: str
    bio: str | None = None
    photo_url: str | None = None
    linkedin_url: str | None = None
    display_order: int = 0


class TeamMemberUpdate(BaseModel):
    full_name: str | None = None
    role_title: str | None = None
    bio: str | None = None
    photo_url: str | None = None
    linkedin_url: str | None = None
    display_order: int | None = None
