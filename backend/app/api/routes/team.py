import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.team import TeamMember
from app.models.user import User
from app.schemas.team import TeamMemberCreate, TeamMemberRead, TeamMemberUpdate

router = APIRouter(prefix="/about-us", tags=["about-us"])
admin_router = APIRouter(prefix="/admin/team", tags=["admin"])


@router.get("/team", response_model=list[TeamMemberRead])
def list_team(db: Session = Depends(get_db)) -> list[TeamMember]:
    """Public -- no auth. This is the About Us page's content."""
    return db.query(TeamMember).order_by(TeamMember.display_order, TeamMember.created_at).all()


@admin_router.get("", response_model=list[TeamMemberRead])
def admin_list_team(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
) -> list[TeamMember]:
    return db.query(TeamMember).order_by(TeamMember.display_order, TeamMember.created_at).all()


@admin_router.post("", response_model=TeamMemberRead, status_code=201)
def create_team_member(
    payload: TeamMemberCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> TeamMember:
    member = TeamMember(**payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@admin_router.patch("/{member_id}", response_model=TeamMemberRead)
def update_team_member(
    member_id: uuid.UUID,
    payload: TeamMemberUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> TeamMember:
    member = db.get(TeamMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(member, field, value)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@admin_router.delete("/{member_id}", status_code=204)
def delete_team_member(
    member_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    member = db.get(TeamMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    db.delete(member)
    db.commit()
