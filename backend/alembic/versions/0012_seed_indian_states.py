"""seed indian states and union territories

Revision ID: 0012
Revises: 0011
Create Date: 2026-09-13

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None

# All 28 states + 8 union territories. This is a small, stable,
# well-known list (unlike districts/schools, which are large and not
# hardcoded here on purpose -- see CLAUDE.md).
STATES_AND_UTS = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi",
    "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
]


def upgrade() -> None:
    states_table = sa.table(
        "states",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String),
    )
    op.bulk_insert(
        states_table, [{"id": uuid.uuid4(), "name": name} for name in STATES_AND_UTS]
    )


def downgrade() -> None:
    names = "', '".join(STATES_AND_UTS)
    op.execute(f"DELETE FROM states WHERE name IN ('{names}')")
