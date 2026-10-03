"""dashboard messages (motivational quotes card)

Revision ID: 0022
Revises: 0021
Create Date: 2026-10-02

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None

ALL_ROLES = ["student", "parent", "mentor", "school_admin", "admin"]


def upgrade() -> None:
    op.create_table(
        "dashboard_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("attribution", sa.String(length=150), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    dashboard_sections = sa.table(
        "dashboard_sections",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("key", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("component_key", sa.String),
    )
    role_dashboard_sections = sa.table(
        "role_dashboard_sections",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("dashboard_section_id", postgresql.UUID(as_uuid=True)),
        sa.column("role", sa.String),
        sa.column("enabled", sa.Boolean),
        sa.column("display_order", sa.Integer),
    )
    dashboard_messages = sa.table(
        "dashboard_messages",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("message", sa.String),
        sa.column("attribution", sa.String),
        sa.column("display_order", sa.Integer),
        sa.column("active", sa.Boolean),
    )

    section_id = uuid.uuid4()
    op.bulk_insert(
        dashboard_sections,
        [
            {
                "id": section_id,
                "key": "motivational_quotes",
                "name": "Motivational Quotes",
                "description": "Short messages the admin writes directly, shown as a card on the dashboard.",
                "component_key": "motivational_quotes_card",
            }
        ],
    )
    op.bulk_insert(
        role_dashboard_sections,
        [
            {
                "id": uuid.uuid4(),
                "dashboard_section_id": section_id,
                "role": role,
                "enabled": True,
                # 4, not 1: welcome=0, ai_assistant=1, continue_learning=2
                # (student only), recent_announcements=3 -- this avoids
                # tying with any of them. Admin can freely reorder via
                # the existing /admin/dashboard-sections UI.
                "display_order": 4,
            }
            for role in ALL_ROLES
        ],
    )
    op.bulk_insert(
        dashboard_messages,
        [
            {
                "id": uuid.uuid4(),
                "message": "The expert in anything was once a beginner.",
                "attribution": None,
                "display_order": 0,
                "active": True,
            },
            {
                "id": uuid.uuid4(),
                "message": "Your career doesn't have to be figured out today — just the next step does.",
                "attribution": None,
                "display_order": 1,
                "active": True,
            },
        ],
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM role_dashboard_sections WHERE dashboard_section_id IN "
        "(SELECT id FROM dashboard_sections WHERE key = 'motivational_quotes')"
    )
    op.execute("DELETE FROM dashboard_sections WHERE key = 'motivational_quotes'")
    op.drop_table("dashboard_messages")
