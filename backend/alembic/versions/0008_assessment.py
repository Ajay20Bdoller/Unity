"""career assessment

Revision ID: 0008
Revises: 0007
Create Date: 2026-09-13

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def _opt(value, label, weights):
    return {"value": value, "label": label, "weights": weights}


QUESTIONS = [
    (
        "Which subject do you enjoy most in school?",
        [
            _opt("a", "Maths / Physics", {"engineering": 2, "technology_ai": 2}),
            _opt("b", "Biology", {"medicine": 3}),
            _opt("c", "History / Civics", {"upsc": 2, "law": 1}),
            _opt("d", "Art / Drawing", {"design": 3}),
            _opt("e", "Business Studies / Economics", {"commerce_ca": 2, "entrepreneurship": 1}),
        ],
    ),
    (
        "What kind of problem do you enjoy solving most?",
        [
            _opt("a", "Building or fixing something", {"engineering": 3}),
            _opt("b", "Helping someone who is unwell", {"medicine": 3}),
            _opt("c", "Arguing a case or resolving a dispute", {"law": 3}),
            _opt("d", "Coming up with a new idea or design", {"design": 2, "entrepreneurship": 2}),
            _opt("e", "Working out numbers and budgets", {"commerce_ca": 3}),
        ],
    ),
    (
        "Pick an activity you'd enjoy on a free afternoon.",
        [
            _opt("a", "Building a small app or website", {"technology_ai": 3}),
            _opt("b", "Reading about a science discovery", {"research_science": 3}),
            _opt("c", "Watching a documentary on government/policy", {"upsc": 2}),
            _opt("d", "Sketching or designing something", {"design": 3}),
            _opt("e", "Fixing a gadget or appliance at home", {"skilled_vocational": 2, "engineering": 1}),
        ],
    ),
    (
        "Which of these sounds most like your ideal workday?",
        [
            _opt("a", "Working in a lab or research setting", {"research_science": 3}),
            _opt("b", "Meeting clients and closing deals", {"commerce_ca": 1, "entrepreneurship": 2}),
            _opt("c", "Treating patients", {"medicine": 3}),
            _opt("d", "Writing code and debugging", {"technology_ai": 3}),
            _opt("e", "Training or drilling as part of a disciplined team", {"defence": 3}),
        ],
    ),
    (
        "What matters most to you in a future career?",
        [
            _opt("a", "Serving the country / public service", {"upsc": 2, "defence": 2}),
            _opt("b", "Creative freedom", {"design": 3}),
            _opt("c", "Financial independence / running my own thing", {"entrepreneurship": 3}),
            _opt("d", "Working with the latest technology", {"technology_ai": 2, "engineering": 1}),
            _opt("e", "Stability and structure", {"commerce_ca": 1, "skilled_vocational": 2}),
        ],
    ),
    (
        "Which school project would you pick if you had a choice?",
        [
            _opt("a", "Build a working model/machine", {"engineering": 3}),
            _opt("b", "Conduct a small science experiment", {"research_science": 2, "medicine": 1}),
            _opt("c", "Debate competition", {"law": 3}),
            _opt("d", "Design a poster or logo", {"design": 3}),
            _opt("e", "Organize a fundraiser or small event", {"entrepreneurship": 2, "commerce_ca": 1}),
        ],
    ),
    (
        "How do you feel about physically demanding, disciplined training?",
        [
            _opt("a", "I'd enjoy that a lot", {"defence": 3}),
            _opt("b", "I prefer working with my hands on practical skills", {"skilled_vocational": 3}),
            _opt("c", "Not really my thing", {}),
        ],
    ),
    (
        "Which sounds more interesting: a courtroom or a hospital ward?",
        [
            _opt("a", "Courtroom", {"law": 3}),
            _opt("b", "Hospital ward", {"medicine": 3}),
            _opt("c", "Neither, I'd rather be in an office or lab", {"research_science": 1, "commerce_ca": 1}),
        ],
    ),
    (
        "You're given a small budget to start something. What do you do?",
        [
            _opt("a", "Start a small business or side hustle", {"entrepreneurship": 3}),
            _opt("b", "Invest it carefully and track the numbers", {"commerce_ca": 3}),
            _opt("c", "Build a prototype of an app idea", {"technology_ai": 2, "engineering": 1}),
            _opt("d", "Fund a community project", {"upsc": 1, "entrepreneurship": 1}),
        ],
    ),
    (
        "Which best describes your favourite way to learn something new?",
        [
            _opt("a", "Hands-on practice and tinkering", {"skilled_vocational": 2, "engineering": 1}),
            _opt("b", "Reading and research", {"research_science": 2, "upsc": 1}),
            _opt("c", "Watching videos and trying it on a computer", {"technology_ai": 2}),
            _opt("d", "Discussing and debating with others", {"law": 2}),
        ],
    ),
]


def upgrade() -> None:
    op.create_table(
        "assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "assessment_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assessments.id"),
            nullable=False,
        ),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("options", postgresql.JSONB(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(
        "ix_assessment_questions_assessment_id", "assessment_questions", ["assessment_id"]
    )

    op.create_table(
        "assessment_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assessments.id"),
            nullable=False,
        ),
        sa.Column(
            "student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("suggested_category_keys", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("raw_scores", postgresql.JSONB(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_assessment_results_assessment_id", "assessment_results", ["assessment_id"])
    op.create_index("ix_assessment_results_student_id", "assessment_results", ["student_id"])

    op.create_table(
        "assessment_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "result_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assessment_results.id"),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assessment_questions.id"),
            nullable=False,
        ),
        sa.Column("selected_option_value", sa.String(length=50), nullable=False),
        sa.UniqueConstraint("result_id", "question_id", name="uq_assessment_response"),
    )
    op.create_index("ix_assessment_responses_result_id", "assessment_responses", ["result_id"])

    # --- seed: one assessment with 10 questions, so it's actually usable ---
    assessment_table = sa.table(
        "assessments",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
    )
    question_table = sa.table(
        "assessment_questions",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("assessment_id", postgresql.UUID(as_uuid=True)),
        sa.column("question_text", sa.Text),
        sa.column("options", postgresql.JSONB()),
        sa.column("display_order", sa.Integer),
    )

    assessment_id = uuid.uuid4()
    op.bulk_insert(
        assessment_table,
        [
            {
                "id": assessment_id,
                "title": "Explore Your Career Interests",
                "description": (
                    "Answer a few quick questions about what you enjoy. This won't tell you "
                    "what to become — it's a starting point for exploring career areas that "
                    "might fit your interests."
                ),
            }
        ],
    )
    op.bulk_insert(
        question_table,
        [
            {
                "id": uuid.uuid4(),
                "assessment_id": assessment_id,
                "question_text": text,
                "options": options,
                "display_order": i,
            }
            for i, (text, options) in enumerate(QUESTIONS)
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_assessment_responses_result_id", table_name="assessment_responses")
    op.drop_table("assessment_responses")

    op.drop_index("ix_assessment_results_student_id", table_name="assessment_results")
    op.drop_index("ix_assessment_results_assessment_id", table_name="assessment_results")
    op.drop_table("assessment_results")

    op.drop_index(
        "ix_assessment_questions_assessment_id", table_name="assessment_questions"
    )
    op.drop_table("assessment_questions")

    op.drop_table("assessments")
