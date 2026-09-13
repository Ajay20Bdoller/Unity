import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin, require_student
from app.db.session import get_db
from app.models.course import Course, Enrollment, Lesson, LessonProgress, Module
from app.models.user import User
from app.schemas.course import (
    ContinueLearningItem,
    CourseCreate,
    CourseDetail,
    CourseDetailWithProgress,
    CourseListItem,
    CourseUpdate,
    EnrollmentRead,
    LessonCreate,
    LessonRead,
    LessonWithProgress,
    ModuleCreate,
    ModuleWithProgress,
    ModuleRead,
)

router = APIRouter(prefix="/courses", tags=["courses"])
student_router = APIRouter(prefix="/students/me", tags=["students"])
admin_router = APIRouter(prefix="/admin/courses", tags=["admin"])


def _course_modules(db: Session, course_id: uuid.UUID) -> list[ModuleRead]:
    modules = (
        db.query(Module).filter(Module.course_id == course_id).order_by(Module.display_order).all()
    )
    result = []
    for module in modules:
        lessons = (
            db.query(Lesson)
            .filter(Lesson.module_id == module.id)
            .order_by(Lesson.display_order)
            .all()
        )
        result.append(
            ModuleRead(
                id=module.id,
                title=module.title,
                display_order=module.display_order,
                lessons=[LessonRead.model_validate(lesson) for lesson in lessons],
            )
        )
    return result


def _course_lesson_ids(db: Session, course_id: uuid.UUID) -> list[uuid.UUID]:
    rows = (
        db.query(Lesson.id)
        .join(Module, Lesson.module_id == Module.id)
        .filter(Module.course_id == course_id)
        .order_by(Module.display_order, Lesson.display_order)
        .all()
    )
    return [r[0] for r in rows]


@router.get("", response_model=list[CourseListItem])
def list_courses(db: Session = Depends(get_db)) -> list[Course]:
    return db.query(Course).filter(Course.published.is_(True)).order_by(Course.title).all()


@router.get("/{slug}", response_model=CourseDetail)
def get_course(slug: str, db: Session = Depends(get_db)) -> CourseDetail:
    course = db.query(Course).filter(Course.slug == slug, Course.published.is_(True)).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return CourseDetail(
        id=course.id,
        slug=course.slug,
        title=course.title,
        description=course.description,
        thumbnail_url=course.thumbnail_url,
        modules=_course_modules(db, course.id),
    )


# --- student enrollment & progress ---


@student_router.get("/courses/{slug}", response_model=CourseDetailWithProgress)
def get_course_with_my_progress(
    slug: str,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> CourseDetailWithProgress:
    course = db.query(Course).filter(Course.slug == slug, Course.published.is_(True)).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    enrolled = (
        db.query(Enrollment)
        .filter(Enrollment.student_id == current_user.id, Enrollment.course_id == course.id)
        .first()
        is not None
    )
    completed_lesson_ids = {
        row[0]
        for row in db.query(LessonProgress.lesson_id)
        .filter(LessonProgress.student_id == current_user.id)
        .all()
    }

    modules = (
        db.query(Module).filter(Module.course_id == course.id).order_by(Module.display_order).all()
    )
    module_reads = []
    for module in modules:
        lessons = (
            db.query(Lesson)
            .filter(Lesson.module_id == module.id)
            .order_by(Lesson.display_order)
            .all()
        )
        module_reads.append(
            ModuleWithProgress(
                id=module.id,
                title=module.title,
                display_order=module.display_order,
                lessons=[
                    LessonWithProgress(
                        **LessonRead.model_validate(lesson).model_dump(),
                        completed=lesson.id in completed_lesson_ids,
                    )
                    for lesson in lessons
                ],
            )
        )

    return CourseDetailWithProgress(
        id=course.id,
        slug=course.slug,
        title=course.title,
        description=course.description,
        thumbnail_url=course.thumbnail_url,
        modules=module_reads,
        enrolled=enrolled,
    )


@student_router.post("/enrollments/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def enroll(
    course_id: uuid.UUID,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> None:
    course = db.get(Course, course_id)
    if not course or not course.published:
        raise HTTPException(status_code=404, detail="Course not found")
    existing = (
        db.query(Enrollment)
        .filter(Enrollment.student_id == current_user.id, Enrollment.course_id == course_id)
        .first()
    )
    if not existing:
        db.add(Enrollment(student_id=current_user.id, course_id=course_id))
        db.commit()


def _progress_for_course(db: Session, student_id: uuid.UUID, course_id: uuid.UUID) -> tuple[int, int]:
    lesson_ids = _course_lesson_ids(db, course_id)
    if not lesson_ids:
        return 0, 0
    completed = (
        db.query(LessonProgress)
        .filter(LessonProgress.student_id == student_id, LessonProgress.lesson_id.in_(lesson_ids))
        .count()
    )
    return completed, len(lesson_ids)


@student_router.get("/enrollments", response_model=list[EnrollmentRead])
def list_my_enrollments(
    current_user: User = Depends(require_student), db: Session = Depends(get_db)
) -> list[EnrollmentRead]:
    rows = db.query(Enrollment, Course).join(Course, Enrollment.course_id == Course.id).filter(
        Enrollment.student_id == current_user.id
    ).all()
    result = []
    for enrollment, course in rows:
        completed, total = _progress_for_course(db, current_user.id, course.id)
        percent = round((completed / total) * 100) if total else 0
        result.append(
            EnrollmentRead(
                course=CourseListItem.model_validate(course),
                enrolled_at=enrollment.enrolled_at.isoformat(),
                total_lessons=total,
                completed_lessons=completed,
                progress_percent=percent,
            )
        )
    return result


@student_router.post("/lessons/{lesson_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
def complete_lesson(
    lesson_id: uuid.UUID,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> None:
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    module = db.get(Module, lesson.module_id)
    enrolled = (
        db.query(Enrollment)
        .filter(Enrollment.student_id == current_user.id, Enrollment.course_id == module.course_id)
        .first()
    )
    if not enrolled:
        raise HTTPException(status_code=400, detail="You must enroll in this course first")

    existing = (
        db.query(LessonProgress)
        .filter(LessonProgress.student_id == current_user.id, LessonProgress.lesson_id == lesson_id)
        .first()
    )
    if not existing:
        db.add(LessonProgress(student_id=current_user.id, lesson_id=lesson_id))
        db.commit()


@student_router.get("/continue-learning", response_model=list[ContinueLearningItem])
def continue_learning(
    current_user: User = Depends(require_student), db: Session = Depends(get_db)
) -> list[ContinueLearningItem]:
    enrollments = (
        db.query(Enrollment, Course).join(Course, Enrollment.course_id == Course.id).filter(
            Enrollment.student_id == current_user.id
        ).all()
    )
    completed_lesson_ids = {
        row[0]
        for row in db.query(LessonProgress.lesson_id)
        .filter(LessonProgress.student_id == current_user.id)
        .all()
    }

    result = []
    for _enrollment, course in enrollments:
        lesson_ids = _course_lesson_ids(db, course.id)
        next_lesson = None
        for lesson_id in lesson_ids:
            if lesson_id not in completed_lesson_ids:
                next_lesson = db.get(Lesson, lesson_id)
                break
        completed_count = sum(1 for lid in lesson_ids if lid in completed_lesson_ids)
        percent = round((completed_count / len(lesson_ids)) * 100) if lesson_ids else 0
        result.append(
            ContinueLearningItem(
                course=CourseListItem.model_validate(course),
                next_lesson=LessonRead.model_validate(next_lesson) if next_lesson else None,
                progress_percent=percent,
            )
        )
    return result


# --- admin CRUD ---


@admin_router.post("", response_model=CourseListItem, status_code=201)
def create_course(
    payload: CourseCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Course:
    if db.query(Course).filter(Course.slug == payload.slug).first():
        raise HTTPException(status_code=409, detail="A course with this slug already exists")
    course = Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@admin_router.patch("/{course_id}", response_model=CourseListItem)
def update_course(
    course_id: uuid.UUID,
    payload: CourseUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Course:
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@admin_router.post("/{course_id}/modules", status_code=201)
def create_module(
    course_id: uuid.UUID,
    payload: ModuleCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    if not db.get(Course, course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    module = Module(course_id=course_id, **payload.model_dump())
    db.add(module)
    db.commit()
    db.refresh(module)
    return {"id": module.id, "title": module.title, "display_order": module.display_order}


@admin_router.post("/modules/{module_id}/lessons", status_code=201)
def create_lesson(
    module_id: uuid.UUID,
    payload: LessonCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> LessonRead:
    if not db.get(Module, module_id):
        raise HTTPException(status_code=404, detail="Module not found")
    lesson = Lesson(module_id=module_id, **payload.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return LessonRead.model_validate(lesson)
