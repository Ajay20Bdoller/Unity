from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.campaign import Campaign, CampaignRegistration
from app.models.career import Career, StudentCareerInterest
from app.models.course import Course, Enrollment
from app.models.mentorship import MentorshipRequest
from app.models.user import User
from app.schemas.admin_stats import AdminActivityStats, RecentUser

router = APIRouter(prefix="/admin/dashboard", tags=["admin"])


@router.get("/stats", response_model=AdminActivityStats)
def get_activity_stats(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
) -> AdminActivityStats:
    users_by_role_rows = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    users_by_role = {role.value: count for role, count in users_by_role_rows}

    mentorship_rows = (
        db.query(MentorshipRequest.status, func.count(MentorshipRequest.id))
        .group_by(MentorshipRequest.status)
        .all()
    )
    mentorship_by_status = {status.value: count for status, count in mentorship_rows}

    recent = db.query(User).order_by(User.created_at.desc()).limit(10).all()

    return AdminActivityStats(
        total_users=sum(users_by_role.values()),
        users_by_role=users_by_role,
        total_careers=db.query(func.count(Career.id)).scalar() or 0,
        total_career_interests=db.query(func.count(StudentCareerInterest.id)).scalar() or 0,
        total_courses=db.query(func.count(Course.id)).scalar() or 0,
        total_enrollments=db.query(func.count(Enrollment.id)).scalar() or 0,
        total_mentorship_requests=sum(mentorship_by_status.values()),
        mentorship_requests_by_status=mentorship_by_status,
        total_campaigns=db.query(func.count(Campaign.id)).scalar() or 0,
        total_campaign_registrations=db.query(func.count(CampaignRegistration.id)).scalar() or 0,
        recent_users=[
            RecentUser(id=u.id, full_name=u.full_name, role=u.role, created_at=u.created_at)
            for u in recent
        ],
    )
