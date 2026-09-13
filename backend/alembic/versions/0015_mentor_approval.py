"""mentor approval status

Revision ID: 0015
Revises: 0014
Create Date: 2026-09-14

"""
import sqlalchemy as sa
from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "mentors",
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("mentors", "is_approved")
