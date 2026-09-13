"""mobile-based login identifier and expanded role-specific registration fields

Revision ID: 0011
Revises: 0010
Create Date: 2026-09-13

"""
import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- users: email becomes optional, mobile_number becomes an
    #     alternate identifier, at least one of the two is required ---
    op.alter_column("users", "email", existing_type=sa.String(length=255), nullable=True)
    op.add_column("users", sa.Column("mobile_number", sa.String(length=20), nullable=True))
    op.create_index("ix_users_mobile_number", "users", ["mobile_number"], unique=True)
    op.create_check_constraint(
        "ck_users_email_or_mobile", "users", "email IS NOT NULL OR mobile_number IS NOT NULL"
    )

    # --- students: mobile_number moves to users; add the fields the
    #     registration form now collects ---
    op.drop_column("students", "mobile_number")
    op.add_column("students", sa.Column("school_name", sa.String(length=255), nullable=True))
    op.add_column("students", sa.Column("address", sa.Text(), nullable=True))
    op.add_column("students", sa.Column("district", sa.String(length=100), nullable=True))
    op.add_column("students", sa.Column("state", sa.String(length=100), nullable=True))
    op.add_column(
        "students",
        sa.Column("country", sa.String(length=100), nullable=True, server_default="India"),
    )
    op.add_column("students", sa.Column("parent_name", sa.String(length=255), nullable=True))
    op.add_column("students", sa.Column("parent_relation", sa.String(length=50), nullable=True))

    # --- parents: mobile_number moves to users; add informational
    #     student_name/relation fields ---
    op.drop_column("parents", "mobile_number")
    op.add_column("parents", sa.Column("student_name", sa.String(length=255), nullable=True))
    op.add_column(
        "parents", sa.Column("relation_to_student", sa.String(length=50), nullable=True)
    )

    # --- mentors: add date_of_birth ---
    op.add_column("mentors", sa.Column("date_of_birth", sa.Date(), nullable=True))

    # --- school_admin_profiles: add date_of_birth, school_name, school_location ---
    op.add_column(
        "school_admin_profiles", sa.Column("date_of_birth", sa.Date(), nullable=True)
    )
    op.add_column(
        "school_admin_profiles", sa.Column("school_name", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "school_admin_profiles",
        sa.Column("school_location", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("school_admin_profiles", "school_location")
    op.drop_column("school_admin_profiles", "school_name")
    op.drop_column("school_admin_profiles", "date_of_birth")

    op.drop_column("mentors", "date_of_birth")

    op.drop_column("parents", "relation_to_student")
    op.drop_column("parents", "student_name")
    op.add_column("parents", sa.Column("mobile_number", sa.String(length=20), nullable=True))

    op.drop_column("students", "parent_relation")
    op.drop_column("students", "parent_name")
    op.drop_column("students", "country")
    op.drop_column("students", "state")
    op.drop_column("students", "district")
    op.drop_column("students", "address")
    op.drop_column("students", "school_name")
    op.add_column("students", sa.Column("mobile_number", sa.String(length=20), nullable=True))

    op.drop_constraint("ck_users_email_or_mobile", "users", type_="check")
    op.drop_index("ix_users_mobile_number", table_name="users")
    op.drop_column("users", "mobile_number")
    op.alter_column("users", "email", existing_type=sa.String(length=255), nullable=False)
