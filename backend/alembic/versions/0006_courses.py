"""courses, modules, lessons, enrollment, progress

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-13

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "courses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("thumbnail_url", sa.String(length=500), nullable=True),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_courses_slug", "courses", ["slug"], unique=True)

    op.create_table(
        "course_translations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=False
        ),
        sa.Column(
            "language_code", sa.String(length=10), sa.ForeignKey("languages.code"), nullable=False
        ),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.UniqueConstraint("course_id", "language_code", name="uq_course_translation"),
    )
    op.create_index("ix_course_translations_course_id", "course_translations", ["course_id"])

    op.create_table(
        "modules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=False
        ),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_modules_course_id", "modules", ["course_id"])

    op.create_table(
        "lessons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "module_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("modules.id"), nullable=False
        ),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column(
            "content_type",
            postgresql.ENUM(
                "video",
                "article",
                "quiz",
                "external_resource",
                name="lesson_content_type",
                create_type=True,
            ),
            nullable=False,
        ),
        sa.Column("content_url", sa.String(length=500), nullable=True),
        sa.Column("content_body", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_lessons_module_id", "lessons", ["module_id"])

    op.create_table(
        "enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=False
        ),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("student_id", "course_id", name="uq_enrollment"),
    )
    op.create_index("ix_enrollments_student_id", "enrollments", ["student_id"])
    op.create_index("ix_enrollments_course_id", "enrollments", ["course_id"])

    op.create_table(
        "lesson_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id"), nullable=False
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("student_id", "lesson_id", name="uq_lesson_progress"),
    )
    op.create_index("ix_lesson_progress_student_id", "lesson_progress", ["student_id"])
    op.create_index("ix_lesson_progress_lesson_id", "lesson_progress", ["lesson_id"])

    # --- seed: one sample published course, so the endpoints and any
    #     frontend built against them have something real to show. Not a
    #     course catalog — that's ongoing content work. ---
    course_table = sa.table(
        "courses",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("slug", sa.String),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
        sa.column("published", sa.Boolean),
    )
    module_table = sa.table(
        "modules",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("course_id", postgresql.UUID(as_uuid=True)),
        sa.column("title", sa.String),
        sa.column("display_order", sa.Integer),
    )
    lesson_table = sa.table(
        "lessons",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("module_id", postgresql.UUID(as_uuid=True)),
        sa.column("title", sa.String),
        sa.column("content_type", sa.String),
        sa.column("content_url", sa.String),
        sa.column("content_body", sa.Text),
        sa.column("display_order", sa.Integer),
    )

    course_id = uuid.uuid4()
    module1_id = uuid.uuid4()
    module2_id = uuid.uuid4()

    op.bulk_insert(
        course_table,
        [
            {
                "id": course_id,
                "slug": "intro-to-programming",
                "title": "Introduction to Programming",
                "description": (
                    "A beginner-friendly first look at what programming is and how to start, "
                    "with no prior experience needed."
                ),
                "published": True,
            }
        ],
    )
    op.bulk_insert(
        module_table,
        [
            {"id": module1_id, "course_id": course_id, "title": "Getting Started", "display_order": 0},
            {
                "id": module2_id,
                "course_id": course_id,
                "title": "Your First Program",
                "display_order": 1,
            },
        ],
    )
    op.bulk_insert(
        lesson_table,
        [
            {
                "id": uuid.uuid4(),
                "module_id": module1_id,
                "title": "What is programming?",
                "content_type": "article",
                "content_url": None,
                "content_body": (
                    "Programming means giving a computer step-by-step instructions to solve a "
                    "problem or do a task. You don't need any special background to start — "
                    "just curiosity and patience to try things out."
                ),
                "display_order": 0,
            },
            {
                "id": uuid.uuid4(),
                "module_id": module1_id,
                "title": "Setting up your first environment",
                "content_type": "external_resource",
                "content_url": "https://www.python.org/about/gettingstarted/",
                "content_body": None,
                "display_order": 1,
            },
            {
                "id": uuid.uuid4(),
                "module_id": module2_id,
                "title": "Writing your first line of code",
                "content_type": "article",
                "content_url": None,
                "content_body": (
                    "Try typing print('Hello, world!') and running it. That's it — you've "
                    "just given the computer its first instruction."
                ),
                "display_order": 0,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_lesson_progress_lesson_id", table_name="lesson_progress")
    op.drop_index("ix_lesson_progress_student_id", table_name="lesson_progress")
    op.drop_table("lesson_progress")

    op.drop_index("ix_enrollments_course_id", table_name="enrollments")
    op.drop_index("ix_enrollments_student_id", table_name="enrollments")
    op.drop_table("enrollments")

    op.drop_index("ix_lessons_module_id", table_name="lessons")
    op.drop_table("lessons")
    op.execute("DROP TYPE lesson_content_type")

    op.drop_index("ix_modules_course_id", table_name="modules")
    op.drop_table("modules")

    op.drop_index("ix_course_translations_course_id", table_name="course_translations")
    op.drop_table("course_translations")

    op.drop_index("ix_courses_slug", table_name="courses")
    op.drop_table("courses")
