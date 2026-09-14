"""Create an admin account.

ADMIN is deliberately not self-registerable via /auth/register (see
app/models/user.py SELF_REGISTERABLE_ROLES) — this script is the
intended way to create the first admin, or any subsequent one, until
an in-app "admin creates another admin" API exists.

Usage (from backend/, with the venv active and DATABASE_URL set):
    python -m scripts.create_admin --email admin@example.com --name "Admin Name" --mobile 9876543210

--mobile is optional but recommended: password reset
(/forgot-password) is mobile-number-only by design (see CLAUDE.md), so
an admin account with no mobile number has no self-service way to
recover a forgotten password.

Prompts for a password interactively (never pass it as a CLI argument —
that would leak into shell history and process listings).
"""
import argparse
import getpass
import sys

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.profiles import SchoolAdminProfile  # noqa: F401 (ensures models are registered)
from app.models.user import User, UserRole


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True, dest="full_name")
    parser.add_argument(
        "--mobile", default=None, help="Recommended — enables /forgot-password for this account"
    )
    args = parser.parse_args()

    password = getpass.getpass("Password (min 8 characters): ")
    if len(password) < 8:
        print("Password must be at least 8 characters long.", file=sys.stderr)
        sys.exit(1)
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords did not match.", file=sys.stderr)
        sys.exit(1)

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == args.email).first():
            print(f"A user with email {args.email} already exists.", file=sys.stderr)
            sys.exit(1)
        if args.mobile and db.query(User).filter(User.mobile_number == args.mobile).first():
            print(f"A user with mobile number {args.mobile} already exists.", file=sys.stderr)
            sys.exit(1)

        user = User(
            email=args.email,
            mobile_number=args.mobile,
            full_name=args.full_name,
            role=UserRole.ADMIN,
            hashed_password=hash_password(password),
        )
        db.add(user)
        db.commit()
        print(f"Admin account created: {args.email}")
        if not args.mobile:
            print(
                "No --mobile given: this account cannot use /forgot-password "
                "if the password is lost. Consider re-running with --mobile.",
                file=sys.stderr,
            )
    finally:
        db.close()


if __name__ == "__main__":
    main()
