import uuid

from pydantic import BaseModel, ConfigDict


class CareerCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    key: str
    name: str
    description: str | None
    display_order: int


class CareerListItem(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    description: str
    category_key: str


class CareerDetail(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    description: str
    eligibility: str | None
    subjects: list[str] | None
    skills: list[str] | None
    entrance_exams: list[str] | None
    education_pathway: str | None
    roadmap: str | None
    category: CareerCategoryRead
    related_careers: list[CareerListItem]
    language: str  # which language these fields are actually in


class CareerCategoryCreate(BaseModel):
    key: str
    name: str
    description: str | None = None
    display_order: int = 0


class CareerCreate(BaseModel):
    category_id: uuid.UUID
    slug: str
    title: str
    description: str
    eligibility: str | None = None
    subjects: list[str] | None = None
    skills: list[str] | None = None
    entrance_exams: list[str] | None = None
    education_pathway: str | None = None
    roadmap: str | None = None


class CareerUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    eligibility: str | None = None
    subjects: list[str] | None = None
    skills: list[str] | None = None
    entrance_exams: list[str] | None = None
    education_pathway: str | None = None
    roadmap: str | None = None


class CareerTranslationUpsert(BaseModel):
    title: str
    description: str
    eligibility: str | None = None
    education_pathway: str | None = None
    roadmap: str | None = None
