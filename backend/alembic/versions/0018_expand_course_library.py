"""expand course library: 2 more courses

Revision ID: 0018
Revises: 0017
Create Date: 2026-09-14

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    courses_table = sa.table(
        "courses",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("slug", sa.String),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
        sa.column("published", sa.Boolean),
    )
    modules_table = sa.table(
        "modules",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("course_id", postgresql.UUID(as_uuid=True)),
        sa.column("title", sa.String),
        sa.column("display_order", sa.Integer),
    )
    lessons_table = sa.table(
        "lessons",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("module_id", postgresql.UUID(as_uuid=True)),
        sa.column("title", sa.String),
        sa.column("content_type", sa.String),
        sa.column("content_url", sa.String),
        sa.column("content_body", sa.Text),
        sa.column("display_order", sa.Integer),
    )

    interview_course_id = uuid.uuid4()
    data_course_id = uuid.uuid4()
    op.bulk_insert(
        courses_table,
        [
            {
                "id": interview_course_id,
                "slug": "interview-communication-skills",
                "title": "Communication Skills for Interviews",
                "description": (
                    "Practical, beginner-friendly habits for coming across clearly and "
                    "confidently in any interview -- school, college, or job."
                ),
                "published": True,
            },
            {
                "id": data_course_id,
                "slug": "intro-to-data-analysis",
                "title": "Introduction to Data Analysis",
                "description": (
                    "A first look at how people make sense of data -- no coding "
                    "experience needed to get started."
                ),
                "published": True,
            },
        ],
    )

    interview_m1 = uuid.uuid4()
    interview_m2 = uuid.uuid4()
    op.bulk_insert(
        modules_table,
        [
            {"id": interview_m1, "course_id": interview_course_id, "title": "Before the interview", "display_order": 0},
            {"id": interview_m2, "course_id": interview_course_id, "title": "During the interview", "display_order": 1},
        ],
    )
    op.bulk_insert(
        lessons_table,
        [
            {
                "id": uuid.uuid4(),
                "module_id": interview_m1,
                "title": "Researching what to expect",
                "content_type": "article",
                "content_url": None,
                "content_body": (
                    "Before any interview, spend 15-20 minutes learning about who you're "
                    "talking to -- a school, a company, a program. What do they care "
                    "about? What's likely to come up? You don't need to memorize answers, "
                    "just walk in less surprised."
                ),
                "display_order": 0,
            },
            {
                "id": uuid.uuid4(),
                "module_id": interview_m1,
                "title": "Practicing out loud",
                "content_type": "article",
                "content_url": None,
                "content_body": (
                    "Thinking through an answer in your head feels very different from "
                    "saying it out loud. Practice answering a few likely questions out "
                    "loud -- to a mirror, a friend, or even just yourself. The goal isn't "
                    "a memorized script, it's getting comfortable hearing your own voice "
                    "say the answer."
                ),
                "display_order": 1,
            },
            {
                "id": uuid.uuid4(),
                "module_id": interview_m2,
                "title": "Answering clearly, without rushing",
                "content_type": "article",
                "content_url": None,
                "content_body": (
                    "It's normal to want to fill silence, but a short pause to think "
                    "before answering reads as confidence, not weakness. Aim to answer "
                    "the actual question asked, in a few clear sentences, before adding "
                    "more detail."
                ),
                "display_order": 0,
            },
            {
                "id": uuid.uuid4(),
                "module_id": interview_m2,
                "title": "Questions to ask them",
                "content_type": "article",
                "content_url": None,
                "content_body": (
                    "Most interviews end with 'do you have any questions for us?' Having "
                    "one or two genuine questions ready -- about the role, the program, "
                    "what a typical day looks like -- shows real interest, not just "
                    "politeness."
                ),
                "display_order": 1,
            },
        ],
    )

    data_m1 = uuid.uuid4()
    op.bulk_insert(
        modules_table,
        [{"id": data_m1, "course_id": data_course_id, "title": "Thinking like an analyst", "display_order": 0}],
    )
    op.bulk_insert(
        lessons_table,
        [
            {
                "id": uuid.uuid4(),
                "module_id": data_m1,
                "title": "What does 'data analysis' actually mean?",
                "content_type": "article",
                "content_url": None,
                "content_body": (
                    "At its core, data analysis is just asking a clear question and "
                    "looking for the answer in numbers or patterns -- 'which product sold "
                    "best?', 'did attendance go up or down?'. You're already doing a "
                    "version of this any time you compare cricket scores or check which "
                    "video got more views."
                ),
                "display_order": 0,
            },
            {
                "id": uuid.uuid4(),
                "module_id": data_m1,
                "title": "Spreadsheets: your first tool",
                "content_type": "external_resource",
                "content_url": "https://support.google.com/docs/answer/6000292",
                "content_body": None,
                "display_order": 1,
            },
            {
                "id": uuid.uuid4(),
                "module_id": data_m1,
                "title": "A question to practice on",
                "content_type": "article",
                "content_url": None,
                "content_body": (
                    "Try this: pick something you track already (pocket money, cricket "
                    "scores, screen time) and write down a week's worth in a simple "
                    "table. Then ask one question about it -- 'which day was highest?' -- "
                    "and answer it just by looking. That's the whole loop: collect, ask, "
                    "answer."
                ),
                "display_order": 2,
            },
        ],
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM lessons WHERE module_id IN "
        "(SELECT id FROM modules WHERE course_id IN "
        "(SELECT id FROM courses WHERE slug IN "
        "('interview-communication-skills', 'intro-to-data-analysis')))"
    )
    op.execute(
        "DELETE FROM modules WHERE course_id IN "
        "(SELECT id FROM courses WHERE slug IN "
        "('interview-communication-skills', 'intro-to-data-analysis'))"
    )
    op.execute(
        "DELETE FROM courses WHERE slug IN "
        "('interview-communication-skills', 'intro-to-data-analysis')"
    )
