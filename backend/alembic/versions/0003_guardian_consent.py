"""guardian relationships and consent records

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-13

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "guardian_relationships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "verified",
                "rejected",
                name="guardian_relationship_status",
                create_type=True,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("student_id", "parent_id", name="uq_guardian_relationship_pair"),
    )
    op.create_index(
        "ix_guardian_relationships_student_id", "guardian_relationships", ["student_id"]
    )
    op.create_index(
        "ix_guardian_relationships_parent_id", "guardian_relationships", ["parent_id"]
    )

    op.create_table(
        "consent_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "guardian_relationship_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("guardian_relationships.id"),
            nullable=False,
        ),
        sa.Column(
            "consent_type",
            postgresql.ENUM(
                "mentorship", "data_sharing", name="consent_type", create_type=True
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "granted",
                "rejected",
                "expired",
                "revoked",
                name="consent_status",
                create_type=True,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_method", sa.String(length=50), nullable=True),
        sa.Column("otp_hash", sa.String(length=64), nullable=True),
        sa.Column("otp_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("otp_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint(
            "guardian_relationship_id", "consent_type", name="uq_consent_relationship_type"
        ),
    )
    op.create_index(
        "ix_consent_records_guardian_relationship_id",
        "consent_records",
        ["guardian_relationship_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_consent_records_guardian_relationship_id", table_name="consent_records"
    )
    op.drop_table("consent_records")
    op.execute("DROP TYPE consent_status")
    op.execute("DROP TYPE consent_type")

    op.drop_index("ix_guardian_relationships_parent_id", table_name="guardian_relationships")
    op.drop_index("ix_guardian_relationships_student_id", table_name="guardian_relationships")
    op.drop_table("guardian_relationships")
    op.execute("DROP TYPE guardian_relationship_status")
