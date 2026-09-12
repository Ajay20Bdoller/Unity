"""auth overhaul: refresh tokens, role-split profiles, languages, locations

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-13

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

LANGUAGES = [
    {"code": "en", "name": "English", "native_name": "English", "is_active": True},
    {"code": "hi", "name": "Hindi", "native_name": "हिन्दी", "is_active": True},
    {"code": "bn", "name": "Bengali", "native_name": "বাংলা", "is_active": True},
    {"code": "te", "name": "Telugu", "native_name": "తెలుగు", "is_active": True},
    {"code": "pa", "name": "Punjabi", "native_name": "ਪੰਜਾਬੀ", "is_active": True},
]


def upgrade() -> None:
    # --- 1. role rename: school -> school_admin (no rows exist yet on
    #        any DB this has actually been applied to; safe rename either
    #        way since it's a catalog-level rename, not a data rewrite) ---
    op.execute("ALTER TYPE user_role RENAME VALUE 'school' TO 'school_admin'")

    # --- 2. languages (seeded directly here — fixed platform config,
    #        not "sample content" seed data) ---
    op.create_table(
        "languages",
        sa.Column("code", sa.String(length=10), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("native_name", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.bulk_insert(
        sa.table(
            "languages",
            sa.column("code", sa.String),
            sa.column("name", sa.String),
            sa.column("native_name", sa.String),
            sa.column("is_active", sa.Boolean),
        ),
        LANGUAGES,
    )

    # FK from users.preferred_language -> languages.code. Safe to add now:
    # every existing row (if any) defaults to 'en', which is seeded above.
    op.create_foreign_key(
        "fk_users_preferred_language",
        "users",
        "languages",
        ["preferred_language"],
        ["code"],
    )

    # --- 3. locations ---
    op.create_table(
        "states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=10), nullable=True),
    )
    op.create_index("ix_states_name", "states", ["name"], unique=True)
    op.create_index("ix_states_code", "states", ["code"], unique=True)

    op.create_table(
        "districts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "state_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("states.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.UniqueConstraint("state_id", "name", name="uq_district_state_name"),
    )
    op.create_index("ix_districts_state_id", "districts", ["state_id"])

    op.create_table(
        "schools",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "state_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("states.id"), nullable=True
        ),
        sa.Column(
            "district_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("districts.id"),
            nullable=True,
        ),
        sa.Column("board", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_schools_name", "schools", ["name"])
    op.create_index("ix_schools_state_id", "schools", ["state_id"])
    op.create_index("ix_schools_district_id", "schools", ["district_id"])

    # --- 4. role-specific profile tables (1:1 with users) ---
    op.create_table(
        "students",
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True
        ),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("class_level", sa.String(length=20), nullable=True),
        sa.Column(
            "school_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("schools.id"), nullable=True
        ),
        sa.Column(
            "state_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("states.id"), nullable=True
        ),
        sa.Column(
            "district_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("districts.id"),
            nullable=True,
        ),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("mobile_number", sa.String(length=20), nullable=True),
        sa.Column("profile_photo_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    op.create_table(
        "parents",
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True
        ),
        sa.Column("mobile_number", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    op.create_table(
        "mentors",
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True
        ),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    op.create_table(
        "school_admin_profiles",
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True
        ),
        sa.Column(
            "school_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("schools.id"), nullable=True
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # --- 5. refresh tokens ---
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index(
        "ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_token_hash", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.drop_table("school_admin_profiles")
    op.drop_table("mentors")
    op.drop_table("parents")
    op.drop_table("students")

    op.drop_index("ix_schools_district_id", table_name="schools")
    op.drop_index("ix_schools_state_id", table_name="schools")
    op.drop_index("ix_schools_name", table_name="schools")
    op.drop_table("schools")

    op.drop_index("ix_districts_state_id", table_name="districts")
    op.drop_table("districts")

    op.drop_index("ix_states_code", table_name="states")
    op.drop_index("ix_states_name", table_name="states")
    op.drop_table("states")

    op.drop_constraint("fk_users_preferred_language", "users", type_="foreignkey")
    op.drop_table("languages")

    op.execute("ALTER TYPE user_role RENAME VALUE 'school_admin' TO 'school'")
