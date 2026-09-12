"""dashboard sections config

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-13

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

ROLES = ["student", "parent", "mentor", "school_admin", "admin"]


def upgrade() -> None:
    op.create_table(
        "dashboard_sections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("component_key", sa.String(length=50), nullable=False),
        sa.Column("default_config", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_dashboard_sections_key", "dashboard_sections", ["key"], unique=True)

    op.create_table(
        "role_dashboard_sections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dashboard_section_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("dashboard_sections.id"),
            nullable=False,
        ),
        # Reuses the existing user_role enum type (created in 0001) —
        # create_type=False is required here, or create_table tries to
        # create user_role a second time and fails (see CLAUDE.md §4).
        sa.Column(
            "role",
            postgresql.ENUM(
                *ROLES, name="user_role", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("config_override", postgresql.JSONB(), nullable=True),
        sa.UniqueConstraint("dashboard_section_id", "role", name="uq_role_dashboard_section"),
    )
    op.create_index(
        "ix_role_dashboard_sections_section_id",
        "role_dashboard_sections",
        ["dashboard_section_id"],
    )

    # --- minimal seed: only sections that actually have something behind
    #     them today. More get added by an admin (or a later migration)
    #     as each feature phase ships — never seed a section that just
    #     shows an empty/fake state. ---
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

    welcome_id = uuid.uuid4()
    ai_assistant_id = uuid.uuid4()

    op.bulk_insert(
        dashboard_sections,
        [
            {
                "id": welcome_id,
                "key": "welcome",
                "name": "Welcome",
                "description": "Profile summary and greeting.",
                "component_key": "welcome_summary",
            },
            {
                "id": ai_assistant_id,
                "key": "ai_assistant",
                "name": "Ask Career AI",
                "description": "Quick answers to career, education and skill questions.",
                "component_key": "ai_assistant_card",
            },
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
                "display_order": order,
            }
            for order, section_id in enumerate([welcome_id, ai_assistant_id])
            for role in ROLES
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_role_dashboard_sections_section_id", table_name="role_dashboard_sections")
    op.drop_table("role_dashboard_sections")
    op.drop_index("ix_dashboard_sections_key", table_name="dashboard_sections")
    op.drop_table("dashboard_sections")
