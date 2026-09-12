import uuid

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole


class DashboardSectionCreate(BaseModel):
    key: str
    name: str
    description: str | None = None
    component_key: str
    default_config: dict | None = None


class DashboardSectionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    component_key: str | None = None
    default_config: dict | None = None


class DashboardSectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    key: str
    name: str
    description: str | None
    component_key: str
    default_config: dict | None


class RoleDashboardSectionUpsert(BaseModel):
    enabled: bool = True
    display_order: int = 0
    config_override: dict | None = None


class RoleDashboardSectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dashboard_section_id: uuid.UUID
    role: UserRole
    enabled: bool
    display_order: int
    config_override: dict | None


class ResolvedDashboardSection(BaseModel):
    """What the frontend section registry actually consumes: one entry
    per section this user's role can see, already merged and ordered."""

    key: str
    component_key: str
    name: str
    config: dict
