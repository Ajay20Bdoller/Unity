import uuid

from pydantic import BaseModel, field_validator


class AssessmentRead(BaseModel):
    id: uuid.UUID
    title: str
    description: str


class PublicOption(BaseModel):
    value: str
    label: str


class PublicQuestion(BaseModel):
    id: uuid.UUID
    question_text: str
    options: list[PublicOption]
    display_order: int


class AssessmentAnswer(BaseModel):
    question_id: uuid.UUID
    selected_option_value: str


class AssessmentSubmission(BaseModel):
    responses: list[AssessmentAnswer]

    @field_validator("responses")
    @classmethod
    def not_empty(cls, value: list[AssessmentAnswer]) -> list[AssessmentAnswer]:
        if not value:
            raise ValueError("At least one response is required")
        return value


class SuggestedCategory(BaseModel):
    key: str
    name: str


class AssessmentResultRead(BaseModel):
    id: uuid.UUID
    assessment_id: uuid.UUID
    suggested_categories: list[SuggestedCategory]
    submitted_at: str
    note: str = (
        "These are exploratory suggestions based on your answers, not a "
        "guarantee or a deterministic career decision — use them as a "
        "starting point to explore, not a final answer."
    )


# --- admin authoring ---


class QuestionOptionCreate(BaseModel):
    value: str
    label: str
    weights: dict[str, int]


class AssessmentQuestionCreate(BaseModel):
    question_text: str
    options: list[QuestionOptionCreate]
    display_order: int = 0


class AssessmentCreate(BaseModel):
    title: str
    description: str
    is_active: bool = True
