import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.mentorship import MentorshipRequestStatus


class MentorProfileUpdate(BaseModel):
    bio: str | None = None
    availability_note: str | None = None


class MentorPublicProfile(BaseModel):
    user_id: uuid.UUID
    full_name: str
    bio: str | None
    availability_note: str | None
    expertise: list[str]  # career category keys
    languages: list[str]  # language codes


class AdminMentorRead(BaseModel):
    user_id: uuid.UUID
    full_name: str
    email: str | None
    mobile_number: str | None
    bio: str | None
    is_approved: bool
    created_at: datetime


class MentorshipRequestCreate(BaseModel):
    mentor_id: uuid.UUID
    message: str


class MentorshipRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    mentor_id: uuid.UUID
    message: str
    status: MentorshipRequestStatus
    requested_at: datetime
    responded_at: datetime | None


class MentorshipSessionCreate(BaseModel):
    scheduled_at: datetime | None = None
    notes: str | None = None


class MentorshipSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mentorship_request_id: uuid.UUID
    scheduled_at: datetime | None
    notes: str | None
    completed: bool


class MentorshipSessionWithContext(MentorshipSessionRead):
    student_id: uuid.UUID
    request_message: str


class MentorshipFeedbackCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comments: str | None = None


class MentorshipFeedbackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    given_by_user_id: uuid.UUID
    rating: int
    comments: str | None
