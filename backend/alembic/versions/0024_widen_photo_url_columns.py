"""widen photo_url columns to text (support uploaded image data URIs)

Revision ID: 0024
Revises: 0023
Create Date: 2026-10-03

"""
import sqlalchemy as sa
from alembic import op

revision = "0024"
down_revision = "0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("students", "profile_photo_url", type_=sa.Text(), existing_nullable=True)
    op.alter_column("mentors", "photo_url", type_=sa.Text(), existing_nullable=True)
    op.alter_column("team_members", "photo_url", type_=sa.Text(), existing_nullable=True)


def downgrade() -> None:
    # Truncating back to varchar(500) would silently corrupt any
    # base64 data URI already stored (longer ones get cut off) -- this
    # direction is destructive, so it's intentionally not attempted
    # automatically. Widening a column is always safe to leave as is.
    pass
