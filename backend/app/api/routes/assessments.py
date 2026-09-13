import uuid
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin, require_student
from app.db.session import get_db
from app.models.assessment import (
    Assessment,
    AssessmentQuestion,
    AssessmentResponse,
    AssessmentResult,
)
from app.models.career import CareerCategory
from app.models.user import User
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentQuestionCreate,
    AssessmentRead,
    AssessmentResultRead,
    AssessmentSubmission,
    PublicOption,
    PublicQuestion,
    SuggestedCategory,
)

router = APIRouter(prefix="/assessments", tags=["assessments"])
student_router = APIRouter(prefix="/students/me/assessments", tags=["students"])
admin_router = APIRouter(prefix="/admin/assessments", tags=["admin"])

TOP_N_SUGGESTIONS = 3


@router.get("", response_model=list[AssessmentRead])
def list_assessments(db: Session = Depends(get_db)) -> list[Assessment]:
    return db.query(Assessment).filter(Assessment.is_active.is_(True)).all()


@router.get("/{assessment_id}/questions", response_model=list[PublicQuestion])
def get_questions(assessment_id: uuid.UUID, db: Session = Depends(get_db)) -> list[PublicQuestion]:
    if not db.query(Assessment).filter(Assessment.id == assessment_id).first():
        raise HTTPException(status_code=404, detail="Assessment not found")
    questions = (
        db.query(AssessmentQuestion)
        .filter(AssessmentQuestion.assessment_id == assessment_id)
        .order_by(AssessmentQuestion.display_order)
        .all()
    )
    return [
        PublicQuestion(
            id=q.id,
            question_text=q.question_text,
            display_order=q.display_order,
            options=[PublicOption(value=o["value"], label=o["label"]) for o in q.options],
        )
        for q in questions
    ]


@student_router.post("/{assessment_id}/submit", response_model=AssessmentResultRead)
def submit_assessment(
    assessment_id: uuid.UUID,
    payload: AssessmentSubmission,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> AssessmentResultRead:
    assessment = db.get(Assessment, assessment_id)
    if not assessment or not assessment.is_active:
        raise HTTPException(status_code=404, detail="Assessment not found")

    questions = {
        q.id: q
        for q in db.query(AssessmentQuestion)
        .filter(AssessmentQuestion.assessment_id == assessment_id)
        .all()
    }
    if set(a.question_id for a in payload.responses) != set(questions.keys()):
        raise HTTPException(
            status_code=400, detail="All questions must be answered exactly once"
        )

    scores: dict[str, int] = defaultdict(int)
    for answer in payload.responses:
        question = questions[answer.question_id]
        option = next(
            (o for o in question.options if o["value"] == answer.selected_option_value), None
        )
        if not option:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid option '{answer.selected_option_value}' for a question",
            )
        for category_key, weight in option.get("weights", {}).items():
            scores[category_key] += weight

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top_keys = [key for key, score in ranked if score > 0][:TOP_N_SUGGESTIONS]

    result = AssessmentResult(
        assessment_id=assessment_id,
        student_id=current_user.id,
        suggested_category_keys=top_keys,
        raw_scores=dict(scores),
    )
    db.add(result)
    db.flush()
    for answer in payload.responses:
        db.add(
            AssessmentResponse(
                result_id=result.id,
                question_id=answer.question_id,
                selected_option_value=answer.selected_option_value,
            )
        )
    db.commit()
    db.refresh(result)

    categories = (
        db.query(CareerCategory).filter(CareerCategory.key.in_(top_keys)).all() if top_keys else []
    )
    category_by_key = {c.key: c for c in categories}
    suggested = [
        SuggestedCategory(key=key, name=category_by_key[key].name)
        for key in top_keys
        if key in category_by_key
    ]

    return AssessmentResultRead(
        id=result.id,
        assessment_id=assessment_id,
        suggested_categories=suggested,
        submitted_at=result.submitted_at.isoformat(),
    )


@student_router.get("/{assessment_id}/results", response_model=list[AssessmentResultRead])
def list_my_results(
    assessment_id: uuid.UUID,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> list[AssessmentResultRead]:
    results = (
        db.query(AssessmentResult)
        .filter(
            AssessmentResult.assessment_id == assessment_id,
            AssessmentResult.student_id == current_user.id,
        )
        .order_by(AssessmentResult.submitted_at.desc())
        .all()
    )
    categories = {c.key: c for c in db.query(CareerCategory).all()}
    return [
        AssessmentResultRead(
            id=r.id,
            assessment_id=r.assessment_id,
            suggested_categories=[
                SuggestedCategory(key=k, name=categories[k].name)
                for k in r.suggested_category_keys
                if k in categories
            ],
            submitted_at=r.submitted_at.isoformat(),
        )
        for r in results
    ]


# --- admin authoring ---


@admin_router.post("", response_model=AssessmentRead, status_code=201)
def create_assessment(
    payload: AssessmentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Assessment:
    assessment = Assessment(**payload.model_dump())
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@admin_router.post("/{assessment_id}/questions", status_code=201)
def add_question(
    assessment_id: uuid.UUID,
    payload: AssessmentQuestionCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    if not db.get(Assessment, assessment_id):
        raise HTTPException(status_code=404, detail="Assessment not found")
    question = AssessmentQuestion(
        assessment_id=assessment_id,
        question_text=payload.question_text,
        options=[o.model_dump() for o in payload.options],
        display_order=payload.display_order,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return {"id": question.id, "question_text": question.question_text}
