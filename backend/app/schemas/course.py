import uuid

from pydantic import BaseModel, ConfigDict

from app.models.course import LessonContentType


class LessonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    content_type: LessonContentType
    content_url: str | None
    content_body: str | None
    display_order: int


class LessonWithProgress(LessonRead):
    completed: bool


class ModuleRead(BaseModel):
    id: uuid.UUID
    title: str
    display_order: int
    lessons: list[LessonRead]


class ModuleWithProgress(BaseModel):
    id: uuid.UUID
    title: str
    display_order: int
    lessons: list[LessonWithProgress]


class CourseListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title: str
    description: str
    thumbnail_url: str | None


class CourseAdminRead(CourseListItem):
    published: bool


class CourseDetail(CourseListItem):
    modules: list[ModuleRead]
    language: str = "en"


class CourseDetailWithProgress(CourseListItem):
    modules: list[ModuleWithProgress]
    enrolled: bool


class EnrollmentRead(BaseModel):
    course: CourseListItem
    enrolled_at: str
    total_lessons: int
    completed_lessons: int
    progress_percent: int


class ContinueLearningItem(BaseModel):
    course: CourseListItem
    next_lesson: LessonRead | None
    progress_percent: int


# --- admin ---


class CourseCreate(BaseModel):
    slug: str
    title: str
    description: str
    thumbnail_url: str | None = None
    published: bool = False


class CourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    thumbnail_url: str | None = None
    published: bool | None = None


class ModuleCreate(BaseModel):
    title: str
    display_order: int = 0


class LessonCreate(BaseModel):
    title: str
    content_type: LessonContentType
    content_url: str | None = None
    content_body: str | None = None
    display_order: int = 0
