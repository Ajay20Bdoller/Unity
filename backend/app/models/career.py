import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CareerCategory(Base):
    __tablename__ = "career_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Career(Base):
    """Exploratory content only — a career page must never read as a
    guarantee. Long-form fields (eligibility, roadmap, ...) are plain
    text here in English; CareerTranslation holds the same fields in
    other languages, never a copy of the English as a fallback row."""

    __tablename__ = "careers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("career_categories.id"), nullable=False, index=True
    )
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    eligibility: Mapped[str | None] = mapped_column(Text, nullable=True)
    subjects: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    skills: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    entrance_exams: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    education_pathway: Mapped[str | None] = mapped_column(Text, nullable=True)
    roadmap: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CareerTranslation(Base):
    __tablename__ = "career_translations"
    __table_args__ = (UniqueConstraint("career_id", "language_code", name="uq_career_translation"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    career_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("careers.id"), nullable=False, index=True
    )
    language_code: Mapped[str] = mapped_column(
        String(10), ForeignKey("languages.code"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    eligibility: Mapped[str | None] = mapped_column(Text, nullable=True)
    education_pathway: Mapped[str | None] = mapped_column(Text, nullable=True)
    roadmap: Mapped[str | None] = mapped_column(Text, nullable=True)


class RelatedCareer(Base):
    __tablename__ = "related_careers"
    __table_args__ = (
        UniqueConstraint("career_id", "related_career_id", name="uq_related_career_pair"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    career_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("careers.id"), nullable=False, index=True
    )
    related_career_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("careers.id"), nullable=False
    )


class StudentCareerInterest(Base):
    __tablename__ = "student_career_interests"
    __table_args__ = (
        UniqueConstraint("student_id", "career_id", name="uq_student_career_interest"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    career_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("careers.id"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
