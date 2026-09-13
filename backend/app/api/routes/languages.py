from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.language import Language
from app.schemas.language import LanguageRead

router = APIRouter(prefix="/languages", tags=["languages"])


@router.get("", response_model=list[LanguageRead])
def list_languages(db: Session = Depends(get_db)) -> list[Language]:
    return db.query(Language).filter(Language.is_active.is_(True)).all()
