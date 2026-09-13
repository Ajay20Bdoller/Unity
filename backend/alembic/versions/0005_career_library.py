"""career library

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-13

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

CATEGORIES = [
    ("engineering", "Engineering", 0),
    ("medicine", "Medicine / NEET", 1),
    ("upsc", "UPSC / Civil Services", 2),
    ("defence", "Defence", 3),
    ("research_science", "Research / Science", 4),
    ("technology_ai", "Technology / AI", 5),
    ("design", "Design", 6),
    ("law", "Law", 7),
    ("commerce_ca", "Commerce / CA", 8),
    ("entrepreneurship", "Entrepreneurship", 9),
    ("skilled_vocational", "Skilled / Vocational", 10),
    ("other", "Other", 11),
]


def upgrade() -> None:
    op.create_table(
        "career_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_career_categories_key", "career_categories", ["key"], unique=True)

    op.create_table(
        "careers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("career_categories.id"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("eligibility", sa.Text(), nullable=True),
        sa.Column("subjects", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("skills", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("entrance_exams", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("education_pathway", sa.Text(), nullable=True),
        sa.Column("roadmap", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_careers_slug", "careers", ["slug"], unique=True)
    op.create_index("ix_careers_category_id", "careers", ["category_id"])

    op.create_table(
        "career_translations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "career_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("careers.id"), nullable=False
        ),
        sa.Column(
            "language_code",
            sa.String(length=10),
            sa.ForeignKey("languages.code"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("eligibility", sa.Text(), nullable=True),
        sa.Column("education_pathway", sa.Text(), nullable=True),
        sa.Column("roadmap", sa.Text(), nullable=True),
        sa.UniqueConstraint("career_id", "language_code", name="uq_career_translation"),
    )
    op.create_index("ix_career_translations_career_id", "career_translations", ["career_id"])

    op.create_table(
        "related_careers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "career_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("careers.id"), nullable=False
        ),
        sa.Column(
            "related_career_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("careers.id"),
            nullable=False,
        ),
        sa.UniqueConstraint("career_id", "related_career_id", name="uq_related_career_pair"),
    )
    op.create_index("ix_related_careers_career_id", "related_careers", ["career_id"])

    op.create_table(
        "student_career_interests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "career_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("careers.id"), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("student_id", "career_id", name="uq_student_career_interest"),
    )
    op.create_index(
        "ix_student_career_interests_student_id", "student_career_interests", ["student_id"]
    )
    op.create_index(
        "ix_student_career_interests_career_id", "student_career_interests", ["career_id"]
    )

    # --- seed: all 12 categories (fixed taxonomy) + a handful of sample
    #     careers so the endpoints have something real to return. This is
    #     nowhere near a full catalog — that's ongoing content work, not
    #     a migration's job. ---
    category_table = sa.table(
        "career_categories",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("key", sa.String),
        sa.column("name", sa.String),
        sa.column("display_order", sa.Integer),
    )
    category_ids = {key: uuid.uuid4() for key, _, _ in CATEGORIES}
    op.bulk_insert(
        category_table,
        [
            {"id": category_ids[key], "key": key, "name": name, "display_order": order}
            for key, name, order in CATEGORIES
        ],
    )

    career_table = sa.table(
        "careers",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("category_id", postgresql.UUID(as_uuid=True)),
        sa.column("slug", sa.String),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
        sa.column("eligibility", sa.Text),
        sa.column("subjects", postgresql.ARRAY(sa.String())),
        sa.column("skills", postgresql.ARRAY(sa.String())),
        sa.column("entrance_exams", postgresql.ARRAY(sa.String())),
        sa.column("education_pathway", sa.Text),
        sa.column("roadmap", sa.Text),
    )

    software_engineer_id = uuid.uuid4()
    doctor_id = uuid.uuid4()
    civil_services_id = uuid.uuid4()
    data_scientist_id = uuid.uuid4()

    op.bulk_insert(
        career_table,
        [
            {
                "id": software_engineer_id,
                "category_id": category_ids["technology_ai"],
                "slug": "software-engineer",
                "title": "Software Engineer",
                "description": (
                    "Software engineers design, build, and maintain the applications and "
                    "systems people use every day — websites, apps, and the services behind them."
                ),
                "eligibility": "Typically a bachelor's degree in Computer Science, IT, or a "
                "related field, though many engineers are self-taught or come from bootcamps.",
                "subjects": ["Mathematics", "Computer Science", "Physics"],
                "skills": ["Programming", "Problem solving", "Logical thinking", "Teamwork"],
                "entrance_exams": ["JEE Main", "JEE Advanced", "State CETs"],
                "education_pathway": "Class 12 (Science, PCM) -> B.Tech/B.E. or BCA -> "
                "internships and personal projects -> entry-level developer role.",
                "roadmap": "Explore: try a beginner coding course. Build: make a couple of "
                "small projects. Learn: pick up one programming language well before spreading "
                "out. Apply: internships are a great way to learn what the job is really like.",
            },
            {
                "id": doctor_id,
                "category_id": category_ids["medicine"],
                "slug": "doctor",
                "title": "Doctor (MBBS)",
                "description": (
                    "Doctors diagnose and treat illness, and work to keep people healthy — in "
                    "hospitals, clinics, and communities."
                ),
                "eligibility": "Class 12 with Physics, Chemistry, Biology, and a qualifying "
                "NEET score for admission to an MBBS program.",
                "subjects": ["Biology", "Chemistry", "Physics"],
                "skills": ["Attention to detail", "Empathy", "Decision-making under pressure"],
                "entrance_exams": ["NEET-UG"],
                "education_pathway": "Class 12 (Science, PCB) -> NEET-UG -> MBBS (5.5 years "
                "incl. internship) -> optional specialization (MD/MS).",
                "roadmap": "This is a long, demanding pathway — talking to a career counselor "
                "or a doctor about day-to-day realities of the profession is a good next step "
                "before committing to it.",
            },
            {
                "id": civil_services_id,
                "category_id": category_ids["upsc"],
                "slug": "civil-services-officer",
                "title": "Civil Services Officer (IAS/IPS/IFS)",
                "description": (
                    "Civil services officers work in public administration — running "
                    "government departments, law and order, foreign affairs, and more."
                ),
                "eligibility": "A bachelor's degree in any discipline, plus qualifying the "
                "UPSC Civil Services Examination (Prelims, Mains, Interview).",
                "subjects": None,
                "skills": ["Analytical thinking", "Communication", "General awareness"],
                "entrance_exams": ["UPSC CSE"],
                "education_pathway": "Any bachelor's degree -> UPSC CSE preparation -> "
                "Prelims -> Mains -> Interview -> training at an academy.",
                "roadmap": "This exam has a low selection rate and typically takes multiple "
                "years of preparation — it helps to have a backup plan alongside it.",
            },
            {
                "id": data_scientist_id,
                "category_id": category_ids["technology_ai"],
                "slug": "data-scientist",
                "title": "Data Scientist",
                "description": (
                    "Data scientists find patterns in data to help organizations make better "
                    "decisions, using statistics, programming, and domain knowledge."
                ),
                "eligibility": "A bachelor's degree in a quantitative field (CS, statistics, "
                "mathematics, engineering) is common, though not the only path in.",
                "subjects": ["Mathematics", "Statistics", "Computer Science"],
                "skills": ["Statistics", "Programming (Python/R)", "Communication"],
                "entrance_exams": ["JEE Main", "JEE Advanced", "State CETs"],
                "education_pathway": "Class 12 (Science, PCM) -> B.Tech/B.Sc -> statistics/ML "
                "coursework or projects -> internships in data/analytics roles.",
                "roadmap": "Explore: try a free intro-to-statistics or Python course. Build: "
                "work through a couple of small datasets end to end. Learn what data scientists "
                "actually spend most of their time on before committing.",
            },
        ],
    )

    related_table = sa.table(
        "related_careers",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("career_id", postgresql.UUID(as_uuid=True)),
        sa.column("related_career_id", postgresql.UUID(as_uuid=True)),
    )
    op.bulk_insert(
        related_table,
        [
            {
                "id": uuid.uuid4(),
                "career_id": software_engineer_id,
                "related_career_id": data_scientist_id,
            },
            {
                "id": uuid.uuid4(),
                "career_id": data_scientist_id,
                "related_career_id": software_engineer_id,
            },
        ],
    )

    translation_table = sa.table(
        "career_translations",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("career_id", postgresql.UUID(as_uuid=True)),
        sa.column("language_code", sa.String),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
    )
    op.bulk_insert(
        translation_table,
        [
            {
                "id": uuid.uuid4(),
                "career_id": software_engineer_id,
                "language_code": "hi",
                "title": "सॉफ्टवेयर इंजीनियर",
                "description": (
                    "सॉफ्टवेयर इंजीनियर वे ऐप्स और सिस्टम डिज़ाइन, निर्माण और बनाए रखते हैं "
                    "जिनका लोग हर दिन उपयोग करते हैं — वेबसाइट, ऐप्स, और उनके पीछे की सेवाएं।"
                ),
            },
        ],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_student_career_interests_career_id", table_name="student_career_interests"
    )
    op.drop_index(
        "ix_student_career_interests_student_id", table_name="student_career_interests"
    )
    op.drop_table("student_career_interests")

    op.drop_index("ix_related_careers_career_id", table_name="related_careers")
    op.drop_table("related_careers")

    op.drop_index("ix_career_translations_career_id", table_name="career_translations")
    op.drop_table("career_translations")

    op.drop_index("ix_careers_category_id", table_name="careers")
    op.drop_index("ix_careers_slug", table_name="careers")
    op.drop_table("careers")

    op.drop_index("ix_career_categories_key", table_name="career_categories")
    op.drop_table("career_categories")
