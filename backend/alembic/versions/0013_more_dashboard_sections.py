"""dashboard sections: continue learning and recent announcements

Revision ID: 0013
Revises: 0012
Create Date: 2026-09-13

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None

ALL_ROLES = ["student", "parent", "mentor", "school_admin", "admin"]


def upgrade() -> None:
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

    continue_learning_id = uuid.uuid4()
    announcements_id = uuid.uuid4()

    op.bulk_insert(
        dashboard_sections,
        [
            {
                "id": continue_learning_id,
                "key": "continue_learning",
                "name": "Continue Learning",
                "description": "Your in-progress courses and the next lesson in each.",
                "component_key": "continue_learning_card",
            },
            {
                "id": announcements_id,
                "key": "recent_announcements",
                "name": "Recent Announcements",
                "description": "The latest announcements relevant to you.",
                "component_key": "recent_announcements_card",
            },
        ],
    )

    op.bulk_insert(
        role_dashboard_sections,
        [
            {
                "id": uuid.uuid4(),
                "dashboard_section_id": continue_learning_id,
                "role": "student",
                "enabled": True,
                "display_order": 2,
            }
        ],
    )

    op.bulk_insert(
        role_dashboard_sections,
        [
            {
                "id": uuid.uuid4(),
                "dashboard_section_id": announcements_id,
                "role": role,
                "enabled": True,
                "display_order": 3,
            }
            for role in ALL_ROLES
        ],
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM role_dashboard_sections WHERE dashboard_section_id IN "
        "(SELECT id FROM dashboard_sections WHERE key IN "
        "('continue_learning', 'recent_announcements'))"
    )
    op.execute(
        "DELETE FROM dashboard_sections WHERE key IN "
        "('continue_learning', 'recent_announcements')"
    )
