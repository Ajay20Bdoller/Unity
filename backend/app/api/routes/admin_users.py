import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/admin/users", tags=["admin"])


class UserActiveUpdate(BaseModel):
    is_active: bool


@router.get("", response_model=list[UserRead])
def list_users(current_user: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch("/{user_id}", response_model=UserRead)
def set_user_active(
    user_id: uuid.UUID,
    payload: UserActiveUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id and not payload.is_active:
        raise HTTPException(status_code=400, detail="You can't deactivate your own account")
    user.is_active = payload.is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
