from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Checks DB connectivity, not just that the process is up -- a
    container that's running but can't reach the database should fail
    a hosting platform's health check (and get restarted/flagged)
    rather than report healthy."""
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
