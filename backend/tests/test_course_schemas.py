import uuid

from app.models.course import LessonContentType
from app.schemas.course import CourseListItem, LessonCreate


def test_course_list_item_round_trips():
    item = CourseListItem(
        id=uuid.uuid4(),
        slug="intro-to-programming",
        title="Introduction to Programming",
        description="Beginner friendly.",
        thumbnail_url=None,
    )
    assert item.slug == "intro-to-programming"


def test_lesson_create_accepts_all_content_types():
    for content_type in LessonContentType:
        payload = LessonCreate(title="A lesson", content_type=content_type)
        assert payload.content_type == content_type
