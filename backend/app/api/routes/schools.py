from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_school_admin
from app.db.session import get_db
from app.models.profiles import SchoolAdminProfile, StudentProfile
from app.models.user import User
from app.schemas.school import SchoolAdminStudentRead

router = APIRouter(prefix="/schools/me", tags=["schools"])


@router.get("/students", response_model=list[SchoolAdminStudentRead])
def list_my_school_students(
    current_user: User = Depends(require_school_admin), db: Session = Depends(get_db)
) -> list[SchoolAdminStudentRead]:
    admin_profile = db.get(SchoolAdminProfile, current_user.id)
    if not admin_profile or not admin_profile.school_name:
        raise HTTPException(
            status_code=400,
            detail="Set your school name on your profile before viewing students",
        )

    # Matched by school name only (free text) -- there's no verified
    # link between a student and a specific institution yet. A typo on
    # either side means a student won't show up here; that's a known
    # limitation, not a bug, until schools become a real structured
    # directory (see CLAUDE.md gaps).
    rows = (
        db.query(User, StudentProfile)
        .join(StudentProfile, StudentProfile.user_id == User.id)
        .filter(StudentProfile.school_name.ilike(admin_profile.school_name))
        .all()
    )
    return [
        SchoolAdminStudentRead(
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
            mobile_number=user.mobile_number,
            class_level=profile.class_level,
            district=profile.district,
            state=profile.state,
        )
        for user, profile in rows
    ]
