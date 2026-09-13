"""password reset requests (mobile-number OTP)

Revision ID: 0014
Revises: 0013
Create Date: 2026-09-13

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "password_reset_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("otp_hash", sa.String(length=64), nullable=False),
        sa.Column("otp_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("otp_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_password_reset_requests_user_id", "password_reset_requests", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_password_reset_requests_user_id", table_name="password_reset_requests"
    )
    op.drop_table("password_reset_requests")
