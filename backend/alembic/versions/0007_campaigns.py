"""campaigns and registrations

Revision ID: 0007
Revises: 0006
Create Date: 2026-09-13

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column(
            "campaign_type",
            postgresql.ENUM(
                "school",
                "coaching",
                "community",
                "online",
                "referral",
                name="campaign_type",
                create_type=True,
            ),
            nullable=False,
        ),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_campaigns_key", "campaigns", ["key"], unique=True)

    op.create_table(
        "campaign_registrations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "campaign_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("campaigns.id"),
            nullable=False,
        ),
        sa.Column(
            "school_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("schools.id"), nullable=True
        ),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_campaign_registrations_user_id", "campaign_registrations", ["user_id"])
    op.create_index(
        "ix_campaign_registrations_campaign_id", "campaign_registrations", ["campaign_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_campaign_registrations_campaign_id", table_name="campaign_registrations"
    )
    op.drop_index("ix_campaign_registrations_user_id", table_name="campaign_registrations")
    op.drop_table("campaign_registrations")

    op.drop_index("ix_campaigns_key", table_name="campaigns")
    op.drop_table("campaigns")
    op.execute("DROP TYPE campaign_type")
