import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.user import UserRole


class RecentUser(BaseModel):
    id: uuid.UUID
    full_name: str
    role: UserRole
    created_at: datetime


class AdminActivityStats(BaseModel):
    total_users: int
    users_by_role: dict[str, int]
    total_careers: int
    total_career_interests: int
    total_courses: int
    total_enrollments: int
    total_mentorship_requests: int
    mentorship_requests_by_status: dict[str, int]
    total_campaigns: int
    total_campaign_registrations: int
    recent_users: list[RecentUser]
