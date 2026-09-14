import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin, require_mentor, require_student
from app.core.consent import student_has_any_active_consent
from app.db.session import get_db
from app.models.career import CareerCategory
from app.models.consent import ConsentType
from app.models.language import Language
from app.models.mentorship import (
    MentorExpertise,
    MentorLanguage,
    MentorshipFeedback,
    MentorshipRequest,
    MentorshipRequestStatus,
    MentorshipSession,
)
from app.models.profiles import MentorProfile
from app.models.user import User, UserRole
from app.schemas.mentorship import (
    AdminMentorRead,
    MentorProfileUpdate,
    MentorPublicProfile,
    MentorshipFeedbackCreate,
    MentorshipFeedbackRead,
    MentorshipRequestCreate,
    MentorshipRequestRead,
    MentorshipSessionCreate,
    MentorshipSessionRead,
    MentorshipSessionWithContext,
)

router = APIRouter(prefix="/mentors", tags=["mentors"])
mentor_router = APIRouter(prefix="/mentors/me", tags=["mentors"])
student_router = APIRouter(prefix="/students/me/mentorship-requests", tags=["students"])
session_router = APIRouter(prefix="/mentorship-sessions", tags=["mentorship"])
admin_router = APIRouter(prefix="/admin/mentors", tags=["admin"])


def _public_profile(db: Session, mentor: User, profile: MentorProfile | None) -> MentorPublicProfile:
    expertise_keys = [
        row[0]
        for row in db.query(CareerCategory.key)
        .join(MentorExpertise, MentorExpertise.career_category_id == CareerCategory.id)
        .filter(MentorExpertise.mentor_id == mentor.id)
        .all()
    ]
    language_codes = [
        row[0]
        for row in db.query(MentorLanguage.language_code)
        .filter(MentorLanguage.mentor_id == mentor.id)
        .all()
    ]
    return MentorPublicProfile(
        user_id=mentor.id,
        full_name=mentor.full_name,
        bio=profile.bio if profile else None,
        availability_note=profile.availability_note if profile else None,
        expertise=expertise_keys,
        languages=language_codes,
    )


@router.get("", response_model=list[MentorPublicProfile])
def list_mentors(
    category: str | None = None, language: str | None = None, db: Session = Depends(get_db)
) -> list[MentorPublicProfile]:
    query = (
        db.query(User)
        .join(MentorProfile, MentorProfile.user_id == User.id)
        .filter(User.role == UserRole.MENTOR, MentorProfile.is_approved.is_(True))
    )
    if category:
        query = query.join(MentorExpertise, MentorExpertise.mentor_id == User.id).join(
            CareerCategory, CareerCategory.id == MentorExpertise.career_category_id
        ).filter(CareerCategory.key == category)
    if language:
        query = query.join(MentorLanguage, MentorLanguage.mentor_id == User.id).filter(
            MentorLanguage.language_code == language
        )
    mentors = query.distinct().all()
    profiles = {p.user_id: p for p in db.query(MentorProfile).all()}
    return [_public_profile(db, m, profiles.get(m.id)) for m in mentors]


@mentor_router.get("", response_model=MentorPublicProfile)
def get_my_profile(
    current_user: User = Depends(require_mentor), db: Session = Depends(get_db)
) -> MentorPublicProfile:
    """A mentor's own view of their profile -- unlike GET /mentors
    (the public list), this works regardless of approval status. An
    unapproved mentor still needs to see and edit their own expertise/
    languages/bio while waiting for admin approval; the public list
    filtering them out until approved shouldn't also blind them to
    their own saved state."""
    profile = db.get(MentorProfile, current_user.id)
    return _public_profile(db, current_user, profile)


@mentor_router.patch("", response_model=MentorPublicProfile)
def update_my_profile(
    payload: MentorProfileUpdate,
    current_user: User = Depends(require_mentor),
    db: Session = Depends(get_db),
) -> MentorPublicProfile:
    profile = db.get(MentorProfile, current_user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.add(profile)
    db.commit()
    return _public_profile(db, current_user, profile)


@mentor_router.post("/expertise/{category_id}", status_code=204)
def add_expertise(
    category_id: uuid.UUID,
    current_user: User = Depends(require_mentor),
    db: Session = Depends(get_db),
) -> None:
    if not db.get(CareerCategory, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    exists = (
        db.query(MentorExpertise)
        .filter(MentorExpertise.mentor_id == current_user.id, MentorExpertise.career_category_id == category_id)
        .first()
    )
    if not exists:
        db.add(MentorExpertise(mentor_id=current_user.id, career_category_id=category_id))
        db.commit()


@mentor_router.post("/languages/{language_code}", status_code=204)
def add_language(
    language_code: str,
    current_user: User = Depends(require_mentor),
    db: Session = Depends(get_db),
) -> None:
    if not db.get(Language, language_code):
        raise HTTPException(status_code=400, detail="Unknown language code")
    exists = (
        db.query(MentorLanguage)
        .filter(MentorLanguage.mentor_id == current_user.id, MentorLanguage.language_code == language_code)
        .first()
    )
    if not exists:
        db.add(MentorLanguage(mentor_id=current_user.id, language_code=language_code))
        db.commit()


# --- requests ---


@student_router.post("", response_model=MentorshipRequestRead, status_code=201)
def create_request(
    payload: MentorshipRequestCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> MentorshipRequest:
    if not student_has_any_active_consent(db, current_user.id, ConsentType.MENTORSHIP):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mentorship requires a parent/guardian to grant mentorship consent first",
        )
    mentor = db.get(User, payload.mentor_id)
    if not mentor or mentor.role != UserRole.MENTOR:
        raise HTTPException(status_code=404, detail="Mentor not found")
    mentor_profile = db.get(MentorProfile, mentor.id)
    if not mentor_profile or not mentor_profile.is_approved:
        # Same 404 as "mentor not found" on purpose — an unapproved
        # mentor shouldn't be distinguishable from a nonexistent one to
        # a student probing IDs directly.
        raise HTTPException(status_code=404, detail="Mentor not found")

    req = MentorshipRequest(student_id=current_user.id, mentor_id=payload.mentor_id, message=payload.message)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@student_router.get("", response_model=list[MentorshipRequestRead])
def list_my_requests(
    current_user: User = Depends(require_student), db: Session = Depends(get_db)
) -> list[MentorshipRequest]:
    return (
        db.query(MentorshipRequest)
        .filter(MentorshipRequest.student_id == current_user.id)
        .order_by(MentorshipRequest.requested_at.desc())
        .all()
    )


@mentor_router.get("/requests", response_model=list[MentorshipRequestRead])
def list_incoming_requests(
    current_user: User = Depends(require_mentor), db: Session = Depends(get_db)
) -> list[MentorshipRequest]:
    return (
        db.query(MentorshipRequest)
        .filter(MentorshipRequest.mentor_id == current_user.id)
        .order_by(MentorshipRequest.requested_at.desc())
        .all()
    )


def _respond(db: Session, mentor_id: uuid.UUID, request_id: uuid.UUID, new_status: MentorshipRequestStatus) -> MentorshipRequest:
    req = db.get(MentorshipRequest, request_id)
    if not req or req.mentor_id != mentor_id:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status != MentorshipRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request has already been responded to")
    req.status = new_status
    req.responded_at = datetime.now(timezone.utc)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@mentor_router.post("/requests/{request_id}/accept", response_model=MentorshipRequestRead)
def accept_request(
    request_id: uuid.UUID, current_user: User = Depends(require_mentor), db: Session = Depends(get_db)
) -> MentorshipRequest:
    return _respond(db, current_user.id, request_id, MentorshipRequestStatus.ACCEPTED)


@mentor_router.post("/requests/{request_id}/decline", response_model=MentorshipRequestRead)
def decline_request(
    request_id: uuid.UUID, current_user: User = Depends(require_mentor), db: Session = Depends(get_db)
) -> MentorshipRequest:
    return _respond(db, current_user.id, request_id, MentorshipRequestStatus.DECLINED)


@mentor_router.post("/requests/{request_id}/sessions", response_model=MentorshipSessionRead, status_code=201)
def create_session(
    request_id: uuid.UUID,
    payload: MentorshipSessionCreate,
    current_user: User = Depends(require_mentor),
    db: Session = Depends(get_db),
) -> MentorshipSession:
    req = db.get(MentorshipRequest, request_id)
    if not req or req.mentor_id != current_user.id:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status != MentorshipRequestStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="Request must be accepted before scheduling a session")

    session = MentorshipSession(mentorship_request_id=request_id, **payload.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@session_router.post("/{session_id}/feedback", response_model=MentorshipFeedbackRead, status_code=201)
def give_feedback(
    session_id: uuid.UUID,
    payload: MentorshipFeedbackCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> MentorshipFeedback:
    session = db.get(MentorshipSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    req = db.get(MentorshipRequest, session.mentorship_request_id)
    if not req or req.student_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    existing = (
        db.query(MentorshipFeedback)
        .filter(MentorshipFeedback.session_id == session_id, MentorshipFeedback.given_by_user_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Feedback already given for this session")

    feedback = MentorshipFeedback(session_id=session_id, given_by_user_id=current_user.id, **payload.model_dump())
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@mentor_router.get("/sessions", response_model=list[MentorshipSessionWithContext])
def list_my_sessions(
    current_user: User = Depends(require_mentor), db: Session = Depends(get_db)
) -> list[MentorshipSessionWithContext]:
    rows = (
        db.query(MentorshipSession, MentorshipRequest)
        .join(MentorshipRequest, MentorshipRequest.id == MentorshipSession.mentorship_request_id)
        .filter(MentorshipRequest.mentor_id == current_user.id)
        .order_by(MentorshipSession.created_at.desc())
        .all()
    )
    return [
        MentorshipSessionWithContext(
            id=session.id,
            mentorship_request_id=session.mentorship_request_id,
            scheduled_at=session.scheduled_at,
            notes=session.notes,
            completed=session.completed,
            student_id=req.student_id,
            request_message=req.message,
        )
        for session, req in rows
    ]


@session_router.post("/{session_id}/complete", response_model=MentorshipSessionRead)
def complete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(require_mentor),
    db: Session = Depends(get_db),
) -> MentorshipSession:
    session = db.get(MentorshipSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    req = db.get(MentorshipRequest, session.mentorship_request_id)
    if not req or req.mentor_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    session.completed = True
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


# --- admin: mentor approval ---


@admin_router.get("", response_model=list[AdminMentorRead])
def list_all_mentors(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
) -> list[AdminMentorRead]:
    rows = (
        db.query(User, MentorProfile)
        .join(MentorProfile, MentorProfile.user_id == User.id)
        .filter(User.role == UserRole.MENTOR)
        .order_by(MentorProfile.is_approved.asc(), User.created_at.desc())
        .all()
    )
    return [
        AdminMentorRead(
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
            mobile_number=user.mobile_number,
            bio=profile.bio,
            is_approved=profile.is_approved,
            created_at=user.created_at,
        )
        for user, profile in rows
    ]


@admin_router.post("/{user_id}/approve", response_model=AdminMentorRead)
def approve_mentor(
    user_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminMentorRead:
    user = db.get(User, user_id)
    profile = db.get(MentorProfile, user_id)
    if not user or user.role != UserRole.MENTOR or not profile:
        raise HTTPException(status_code=404, detail="Mentor not found")

    profile.is_approved = True
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return AdminMentorRead(
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        mobile_number=user.mobile_number,
        bio=profile.bio,
        is_approved=profile.is_approved,
        created_at=user.created_at,
    )


@admin_router.post("/{user_id}/unapprove", response_model=AdminMentorRead)
def unapprove_mentor(
    user_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminMentorRead:
    user = db.get(User, user_id)
    profile = db.get(MentorProfile, user_id)
    if not user or user.role != UserRole.MENTOR or not profile:
        raise HTTPException(status_code=404, detail="Mentor not found")

    profile.is_approved = False
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return AdminMentorRead(
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        mobile_number=user.mobile_number,
        bio=profile.bio,
        is_approved=profile.is_approved,
        created_at=user.created_at,
    )
