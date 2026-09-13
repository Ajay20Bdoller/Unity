"""announcements

Revision ID: 0010
Revises: 0009
Create Date: 2026-09-13

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "announcements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("audience", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "language_code",
            sa.String(length=10),
            sa.ForeignKey("languages.code"),
            nullable=False,
            server_default="en",
        ),
        sa.Column(
            "publish_status",
            postgresql.ENUM("draft", "published", name="publish_status", create_type=True),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("announcements")
    op.execute("DROP TYPE publish_status")
