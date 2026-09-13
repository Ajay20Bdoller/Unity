import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin, require_student
from app.db.session import get_db
from app.models.career import (
    Career,
    CareerCategory,
    CareerTranslation,
    RelatedCareer,
    StudentCareerInterest,
)
from app.models.language import Language
from app.models.user import User
from app.schemas.career import (
    CareerCategoryCreate,
    CareerCategoryRead,
    CareerCreate,
    CareerDetail,
    CareerListItem,
    CareerTranslationUpsert,
    CareerUpdate,
)

router = APIRouter(prefix="/careers", tags=["careers"])
student_router = APIRouter(prefix="/students/me/career-interests", tags=["students"])
admin_router = APIRouter(prefix="/admin/careers", tags=["admin"])


def _to_list_item(career: Career, category_key: str) -> CareerListItem:
    return CareerListItem(
        id=career.id,
        slug=career.slug,
        title=career.title,
        description=career.description,
        category_key=category_key,
    )


@router.get("/categories", response_model=list[CareerCategoryRead])
def list_categories(db: Session = Depends(get_db)) -> list[CareerCategory]:
    return db.query(CareerCategory).order_by(CareerCategory.display_order).all()


@router.get("", response_model=list[CareerListItem])
def list_careers(
    category: str | None = Query(default=None, description="Category key to filter by"),
    q: str | None = Query(default=None, description="Search career titles"),
    db: Session = Depends(get_db),
) -> list[CareerListItem]:
    query = db.query(Career, CareerCategory).join(
        CareerCategory, Career.category_id == CareerCategory.id
    )
    if category:
        query = query.filter(CareerCategory.key == category)
    if q:
        query = query.filter(Career.title.ilike(f"%{q}%"))
    rows = query.order_by(Career.title).all()
    return [_to_list_item(career, cat.key) for career, cat in rows]


@router.get("/{slug}", response_model=CareerDetail)
def get_career(
    slug: str,
    lang: str = Query(default="en"),
    db: Session = Depends(get_db),
) -> CareerDetail:
    career = db.query(Career).filter(Career.slug == slug).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
    category = db.get(CareerCategory, career.category_id)

    title, description, eligibility, education_pathway, roadmap = (
        career.title,
        career.description,
        career.eligibility,
        career.education_pathway,
        career.roadmap,
    )
    resolved_language = "en"
    if lang != "en":
        translation = (
            db.query(CareerTranslation)
            .filter(CareerTranslation.career_id == career.id, CareerTranslation.language_code == lang)
            .first()
        )
        if translation:
            title, description = translation.title, translation.description
            eligibility = translation.eligibility
            education_pathway = translation.education_pathway
            roadmap = translation.roadmap
            resolved_language = lang
        # else: silently fall back to English — no raw missing-translation
        # error, no empty fields (doc-21 §13: missing translations fall
        # back to English, never show a broken/empty page).

    related_rows = (
        db.query(Career, CareerCategory)
        .join(RelatedCareer, RelatedCareer.related_career_id == Career.id)
        .join(CareerCategory, Career.category_id == CareerCategory.id)
        .filter(RelatedCareer.career_id == career.id)
        .all()
    )

    return CareerDetail(
        id=career.id,
        slug=career.slug,
        title=title,
        description=description,
        eligibility=eligibility,
        subjects=career.subjects,
        skills=career.skills,
        entrance_exams=career.entrance_exams,
        education_pathway=education_pathway,
        roadmap=roadmap,
        category=category,
        related_careers=[_to_list_item(c, cat.key) for c, cat in related_rows],
        language=resolved_language,
    )


# --- student career interests ---


@student_router.get("", response_model=list[CareerListItem])
def list_my_interests(
    current_user: User = Depends(require_student), db: Session = Depends(get_db)
) -> list[CareerListItem]:
    rows = (
        db.query(Career, CareerCategory)
        .join(StudentCareerInterest, StudentCareerInterest.career_id == Career.id)
        .join(CareerCategory, Career.category_id == CareerCategory.id)
        .filter(StudentCareerInterest.student_id == current_user.id)
        .all()
    )
    return [_to_list_item(c, cat.key) for c, cat in rows]


@student_router.post("/{career_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_interest(
    career_id: uuid.UUID,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> None:
    if not db.get(Career, career_id):
        raise HTTPException(status_code=404, detail="Career not found")
    existing = (
        db.query(StudentCareerInterest)
        .filter(
            StudentCareerInterest.student_id == current_user.id,
            StudentCareerInterest.career_id == career_id,
        )
        .first()
    )
    if not existing:
        db.add(StudentCareerInterest(student_id=current_user.id, career_id=career_id))
        db.commit()


@student_router.delete("/{career_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_interest(
    career_id: uuid.UUID,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> None:
    row = (
        db.query(StudentCareerInterest)
        .filter(
            StudentCareerInterest.student_id == current_user.id,
            StudentCareerInterest.career_id == career_id,
        )
        .first()
    )
    if row:
        db.delete(row)
        db.commit()


# --- admin CRUD ---


@admin_router.post("/categories", response_model=CareerCategoryRead, status_code=201)
def create_category(
    payload: CareerCategoryCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> CareerCategory:
    if db.query(CareerCategory).filter(CareerCategory.key == payload.key).first():
        raise HTTPException(status_code=409, detail="A category with this key already exists")
    category = CareerCategory(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@admin_router.post("", response_model=CareerListItem, status_code=201)
def create_career(
    payload: CareerCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> CareerListItem:
    category = db.get(CareerCategory, payload.category_id)
    if not category:
        raise HTTPException(status_code=400, detail="Unknown category_id")
    if db.query(Career).filter(Career.slug == payload.slug).first():
        raise HTTPException(status_code=409, detail="A career with this slug already exists")

    career = Career(**payload.model_dump())
    db.add(career)
    db.commit()
    db.refresh(career)
    return _to_list_item(career, category.key)


@admin_router.patch("/{career_id}", response_model=CareerListItem)
def update_career(
    career_id: uuid.UUID,
    payload: CareerUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> CareerListItem:
    career = db.get(Career, career_id)
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(career, field, value)
    db.add(career)
    db.commit()
    db.refresh(career)
    category = db.get(CareerCategory, career.category_id)
    return _to_list_item(career, category.key)


@admin_router.put("/{career_id}/translations/{language_code}", status_code=204)
def upsert_translation(
    career_id: uuid.UUID,
    language_code: str,
    payload: CareerTranslationUpsert,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    if not db.get(Career, career_id):
        raise HTTPException(status_code=404, detail="Career not found")
    if not db.get(Language, language_code):
        raise HTTPException(status_code=400, detail="Unknown language code")

    row = (
        db.query(CareerTranslation)
        .filter(
            CareerTranslation.career_id == career_id,
            CareerTranslation.language_code == language_code,
        )
        .first()
    )
    if not row:
        row = CareerTranslation(career_id=career_id, language_code=language_code)
    for field, value in payload.model_dump().items():
        setattr(row, field, value)
    db.add(row)
    db.commit()


@admin_router.put("/{career_id}/related/{related_career_id}", status_code=204)
def add_related_career(
    career_id: uuid.UUID,
    related_career_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    if career_id == related_career_id:
        raise HTTPException(status_code=400, detail="A career cannot be related to itself")
    if not db.get(Career, career_id) or not db.get(Career, related_career_id):
        raise HTTPException(status_code=404, detail="Career not found")

    existing = (
        db.query(RelatedCareer)
        .filter(
            RelatedCareer.career_id == career_id,
            RelatedCareer.related_career_id == related_career_id,
        )
        .first()
    )
    if not existing:
        db.add(RelatedCareer(career_id=career_id, related_career_id=related_career_id))
        db.commit()
