"""mentorship foundation

Revision ID: 0009
Revises: 0008
Create Date: 2026-09-13

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("mentors", sa.Column("availability_note", sa.String(length=300), nullable=True))

    op.create_table(
        "mentor_expertise",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "mentor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "career_category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("career_categories.id"),
            nullable=False,
        ),
        sa.UniqueConstraint("mentor_id", "career_category_id", name="uq_mentor_expertise"),
    )
    op.create_index("ix_mentor_expertise_mentor_id", "mentor_expertise", ["mentor_id"])

    op.create_table(
        "mentor_languages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "mentor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "language_code", sa.String(length=10), sa.ForeignKey("languages.code"), nullable=False
        ),
        sa.UniqueConstraint("mentor_id", "language_code", name="uq_mentor_language"),
    )
    op.create_index("ix_mentor_languages_mentor_id", "mentor_languages", ["mentor_id"])

    op.create_table(
        "mentorship_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "mentor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "accepted",
                "declined",
                "completed",
                name="mentorship_request_status",
                create_type=True,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_mentorship_requests_student_id", "mentorship_requests", ["student_id"])
    op.create_index("ix_mentorship_requests_mentor_id", "mentorship_requests", ["mentor_id"])

    op.create_table(
        "mentorship_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "mentorship_request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mentorship_requests.id"),
            nullable=False,
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_mentorship_sessions_request_id", "mentorship_sessions", ["mentorship_request_id"]
    )

    op.create_table(
        "mentorship_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mentorship_sessions.id"),
            nullable=False,
        ),
        sa.Column(
            "given_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("session_id", "given_by_user_id", name="uq_mentorship_feedback"),
    )
    op.create_index("ix_mentorship_feedback_session_id", "mentorship_feedback", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_mentorship_feedback_session_id", table_name="mentorship_feedback")
    op.drop_table("mentorship_feedback")

    op.drop_index("ix_mentorship_sessions_request_id", table_name="mentorship_sessions")
    op.drop_table("mentorship_sessions")

    op.drop_index("ix_mentorship_requests_mentor_id", table_name="mentorship_requests")
    op.drop_index("ix_mentorship_requests_student_id", table_name="mentorship_requests")
    op.drop_table("mentorship_requests")
    op.execute("DROP TYPE mentorship_request_status")

    op.drop_index("ix_mentor_languages_mentor_id", table_name="mentor_languages")
    op.drop_table("mentor_languages")

    op.drop_index("ix_mentor_expertise_mentor_id", table_name="mentor_expertise")
    op.drop_table("mentor_expertise")

    op.drop_column("mentors", "availability_note")
