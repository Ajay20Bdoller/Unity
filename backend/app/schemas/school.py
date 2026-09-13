import uuid

from pydantic import BaseModel


class SchoolAdminStudentRead(BaseModel):
    user_id: uuid.UUID
    full_name: str
    email: str | None
    mobile_number: str | None
    class_level: str | None
    district: str | None
    state: str | None
