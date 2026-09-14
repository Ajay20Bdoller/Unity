import uuid
from collections.abc import Callable

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    if not access_token:
        raise credentials_error

    payload = decode_access_token(access_token)
    if not payload or "sub" not in payload:
        raise credentials_error

    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError):
        raise credentials_error

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise credentials_error

    # A password change (or reset) revokes refresh tokens, but that
    # alone doesn't invalidate an access token issued before it — a
    # stateless JWT keeps working until it naturally expires (now up
    # to 7 days) regardless. Rejecting any token issued before the
    # last password change closes that gap: changing your password
    # actually locks out a token someone else may have gotten hold of,
    # not just refresh renewal. `iat` may be absent on tokens issued
    # before this check existed — treat that as unverifiable rather
    # than reject, so deploying this doesn't itself log everyone out.
    # Compare as whole-second Unix timestamps on both sides: JWT `iat`
    # is inherently truncated to whole seconds (standard JWT numeric
    # date format has no sub-second part), so comparing it against
    # password_changed_at's microsecond precision directly would
    # falsely reject a token issued in the very same second as the
    # password change — int(...timestamp()) truncates the same way on
    # both sides instead of comparing mismatched precision.
    issued_at = payload.get("iat")
    if issued_at is not None:
        password_changed_at_ts = int(user.password_changed_at.timestamp())
        if int(issued_at) < password_changed_at_ts:
            raise credentials_error

    return user


def require_role(*roles: UserRole) -> Callable[[User], User]:
    """Dependency factory: require_role(UserRole.ADMIN) etc. Frontend role
    info is never trusted for this — it always re-checks against the
    authenticated user resolved from the access token."""

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource",
            )
        return current_user

    return dependency


require_student = require_role(UserRole.STUDENT)
require_parent = require_role(UserRole.PARENT)
require_mentor = require_role(UserRole.MENTOR)
require_school_admin = require_role(UserRole.SCHOOL_ADMIN)
require_admin = require_role(UserRole.ADMIN)
