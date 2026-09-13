from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.location import State
from app.schemas.location import StateRead

router = APIRouter(prefix="/states", tags=["locations"])


@router.get("", response_model=list[StateRead])
def list_states(db: Session = Depends(get_db)) -> list[State]:
    return db.query(State).order_by(State.name).all()
