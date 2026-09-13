import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class LessonContentType(str, enum.Enum):
    VIDEO = "video"
    ARTICLE = "article"
    QUIZ = "quiz"
    EXTERNAL_RESOURCE = "external_resource"


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CourseTranslation(Base):
    __tablename__ = "course_translations"
    __table_args__ = (UniqueConstraint("course_id", "language_code", name="uq_course_translation"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False, index=True
    )
    language_code: Mapped[str] = mapped_column(
        String(10), ForeignKey("languages.code"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Lesson(Base):
    """content_url is used for VIDEO (an embed/link, never a re-uploaded
    copy of someone else's video) and EXTERNAL_RESOURCE; content_body
    holds the actual text for ARTICLE. QUIZ lessons are a content-type
    marker only in this phase — no structured question builder for
    lesson-level quizzes yet (that overlaps with the separate Assessment
    feature; not duplicated here on purpose)."""

    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("modules.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content_type: Mapped[LessonContentType] = mapped_column(
        Enum(
            LessonContentType,
            name="lesson_content_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    content_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_enrollment"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False, index=True
    )
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("student_id", "lesson_id", name="uq_lesson_progress"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False, index=True
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
