"""mentor photo_url

Revision ID: 0021
Revises: 0020
Create Date: 2026-10-02

"""
import sqlalchemy as sa
from alembic import op

revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("mentors", sa.Column("photo_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("mentors", "photo_url")
