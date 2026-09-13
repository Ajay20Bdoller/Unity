import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.announcement import Announcement, PublishStatus
from app.models.user import User
from app.schemas.announcement import (
    AnnouncementAdminRead,
    AnnouncementCreate,
    AnnouncementRead,
    AnnouncementUpdate,
)

router = APIRouter(prefix="/announcements", tags=["announcements"])
admin_router = APIRouter(prefix="/admin/announcements", tags=["admin"])


@router.get("", response_model=list[AnnouncementRead])
def list_my_announcements(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Announcement]:
    base = db.query(Announcement).filter(
        Announcement.publish_status == PublishStatus.PUBLISHED,
        or_(Announcement.audience.is_(None), Announcement.audience.any(current_user.role.value)),
    )
    in_language = base.filter(Announcement.language_code == current_user.preferred_language).all()
    if in_language or current_user.preferred_language == "en":
        return sorted(in_language, key=lambda a: a.published_at or a.created_at, reverse=True)
    # Fall back to English if nothing exists in the reader's language.
    fallback = base.filter(Announcement.language_code == "en").all()
    return sorted(fallback, key=lambda a: a.published_at or a.created_at, reverse=True)


@admin_router.get("", response_model=list[AnnouncementAdminRead])
def list_all(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
) -> list[Announcement]:
    return db.query(Announcement).order_by(Announcement.created_at.desc()).all()


@admin_router.post("", response_model=AnnouncementAdminRead, status_code=201)
def create_announcement(
    payload: AnnouncementCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Announcement:
    announcement = Announcement(**payload.model_dump())
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


@admin_router.patch("/{announcement_id}", response_model=AnnouncementAdminRead)
def update_announcement(
    announcement_id: uuid.UUID,
    payload: AnnouncementUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Announcement:
    announcement = db.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(announcement, field, value)
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


@admin_router.post("/{announcement_id}/publish", response_model=AnnouncementAdminRead)
def publish_announcement(
    announcement_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Announcement:
    announcement = db.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    announcement.publish_status = PublishStatus.PUBLISHED
    announcement.published_at = datetime.now(timezone.utc)
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement
