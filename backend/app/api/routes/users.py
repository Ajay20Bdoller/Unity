from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.language import Language
from app.models.user import User
from app.schemas.user import LanguageUpdate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me/language", response_model=UserRead)
def update_preferred_language(
    payload: LanguageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    language = (
        db.query(Language)
        .filter(Language.code == payload.preferred_language, Language.is_active.is_(True))
        .first()
    )
    if not language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported language code",
        )

    current_user.preferred_language = payload.preferred_language
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
