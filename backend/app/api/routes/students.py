from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_student
from app.db.session import get_db
from app.models.guardian import GuardianRelationship, GuardianRelationshipStatus
from app.models.location import District, School, State
from app.models.profiles import StudentProfile
from app.models.user import User, UserRole
from app.schemas.guardian import GuardianInviteRequest, GuardianRelationshipRead
from app.schemas.student import StudentProfileRead, StudentProfileUpdate

router = APIRouter(prefix="/students", tags=["students"])


def _get_or_404(db: Session, user_id) -> StudentProfile:
    profile = db.get(StudentProfile, user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    return profile


@router.get("/me", response_model=StudentProfileRead)
def read_my_profile(
    current_user: User = Depends(require_student), db: Session = Depends(get_db)
) -> StudentProfile:
    return _get_or_404(db, current_user.id)


@router.patch("/me", response_model=StudentProfileRead)
def update_my_profile(
    payload: StudentProfileUpdate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> StudentProfile:
    profile = _get_or_404(db, current_user.id)
    updates = payload.model_dump(exclude_unset=True)

    if "school_id" in updates and updates["school_id"] is not None:
        if not db.get(School, updates["school_id"]):
            raise HTTPException(status_code=400, detail="Unknown school_id")
    if "state_id" in updates and updates["state_id"] is not None:
        if not db.get(State, updates["state_id"]):
            raise HTTPException(status_code=400, detail="Unknown state_id")
    if "district_id" in updates and updates["district_id"] is not None:
        if not db.get(District, updates["district_id"]):
            raise HTTPException(status_code=400, detail="Unknown district_id")

    for field, value in updates.items():
        setattr(profile, field, value)

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.post(
    "/me/guardians",
    response_model=GuardianRelationshipRead,
    status_code=status.HTTP_201_CREATED,
)
def invite_guardian(
    payload: GuardianInviteRequest,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> GuardianRelationship:
    parent = db.query(User).filter(User.email == payload.parent_email).first()
    if not parent or parent.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No parent account found with that email",
        )

    existing = (
        db.query(GuardianRelationship)
        .filter(
            GuardianRelationship.student_id == current_user.id,
            GuardianRelationship.parent_id == parent.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A guardian relationship with this parent already exists",
        )

    relationship = GuardianRelationship(
        student_id=current_user.id,
        parent_id=parent.id,
        status=GuardianRelationshipStatus.PENDING,
    )
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    return relationship


@router.get("/me/guardians", response_model=list[GuardianRelationshipRead])
def list_my_guardians(
    current_user: User = Depends(require_student), db: Session = Depends(get_db)
) -> list[GuardianRelationship]:
    return (
        db.query(GuardianRelationship)
        .filter(GuardianRelationship.student_id == current_user.id)
        .order_by(GuardianRelationship.created_at.desc())
        .all()
    )
