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
