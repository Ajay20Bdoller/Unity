"""repair: re-seed reference/catalog data if missing (idempotent)

Revision ID: 0025
Revises: 0024
Create Date: 2026-10-03

Every INSERT in this migration uses ON CONFLICT DO NOTHING on each
table's natural unique key, making the whole migration safe to design
as a repair: if a table's seed rows are present (the normal case),
nothing happens; if they are missing (a table got cleared outside of
alembic -- a manual TRUNCATE, a database reset, anything that doesn't
also roll back alembic_version), this re-inserts them without
duplicating anything that is still there and without needing a risky
downgrade through the whole migration chain, which would also reverse
every schema change along the way.

Covers: languages (5), career_categories (12), careers (16: the 4
original + the 12 added in 0017), and the dashboard_sections catalog
rows + role_dashboard_sections enablement for welcome/ai_assistant
(0004) and continue_learning/recent_announcements (0013) -- the
motivational_quotes section from 0022 is untouched here since, if it
needed this same repair, it would not have been visible in the first
place (the report this migration responds to was specifically that
newer seed data was intact while older seed data was not).
"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert as pg_insert

revision = "0025"
down_revision = "0024"
branch_labels = None
depends_on = None

LANGUAGES = [
    {"code": "en", "name": "English", "native_name": "English", "is_active": True},
    {"code": "hi", "name": "Hindi", "native_name": "हिन्दी", "is_active": True},
    {"code": "bn", "name": "Bengali", "native_name": "বাংলা", "is_active": True},
    {"code": "te", "name": "Telugu", "native_name": "తెలుగు", "is_active": True},
    {"code": "pa", "name": "Punjabi", "native_name": "ਪੰਜਾਬੀ", "is_active": True},
]

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

ORIGINAL_CAREERS = [
    {
        "category_key": "technology_ai",
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
        "category_key": "medicine",
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
        "category_key": "upsc",
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
        "category_key": "technology_ai",
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
]

NEW_CAREERS = [{'category_key': 'defence', 'slug': 'army-officer', 'title': 'Army Officer', 'description': 'Officers lead soldiers and manage operations in the Indian Army — a mix of leadership, discipline, and technical roles across infantry, engineering, medical, and other branches.', 'eligibility': "After Class 12 via NDA, or after a bachelor's degree via CDS — age and physical fitness criteria apply.", 'subjects': ['Mathematics', 'Physics', 'English'], 'skills': ['Leadership', 'Physical fitness', 'Decision-making under pressure', 'Teamwork'], 'entrance_exams': ['NDA', 'CDS', 'SSB Interview'], 'education_pathway': "Class 12 -> NDA written exam + SSB interview -> National Defence Academy (3 years) -> Indian Military Academy -> commissioned officer. (Or: bachelor's degree -> CDS -> IMA/OTA.)", 'roadmap': "Explore: read about the different Army branches (infantry, engineers, signals, medical). Build: work on physical fitness early — the SSB tests both mind and body. Learn: NDA exam covers maths, English, and general knowledge. Apply: practice previous years' NDA papers and mock SSB interviews."}, {'category_key': 'research_science', 'slug': 'research-scientist', 'title': 'Research Scientist', 'description': 'Research scientists investigate open questions in a field — designing experiments, analyzing data, and publishing findings that push knowledge forward, in universities, government labs, or industry R&D.', 'eligibility': "Bachelor's degree in a science field, followed by a master's and usually a PhD for independent research roles.", 'subjects': ['Physics', 'Chemistry', 'Biology', 'Mathematics'], 'skills': ['Curiosity', 'Patience', 'Data analysis', 'Scientific writing'], 'entrance_exams': ["JEE/NEET (for the bachelor's degree)", 'CSIR-NET', 'GATE', 'JEST'], 'education_pathway': 'Class 12 (Science) -> B.Sc. in a chosen subject -> M.Sc. -> PhD (often funded, with a stipend) -> postdoctoral research -> scientist/faculty position.', 'roadmap': 'Explore: read popular science writing in an area that interests you. Build: try a school or college science fair project. Learn: a strong foundation in one subject matters more than breadth early on. Apply: summer research internships (many institutes run them) are the best way to see if research suits you.'}, {'category_key': 'design', 'slug': 'ux-ui-designer', 'title': 'UX/UI Designer', 'description': 'UX/UI designers shape how apps and websites look and feel — researching what users need, sketching layouts, and testing whether the result is actually easy to use.', 'eligibility': "A design degree helps but isn't mandatory — many designers build a portfolio through self-study, bootcamps, or a related degree (like Computer Science or Psychology) plus design courses.", 'subjects': ['Art/Design', 'Computer Science', 'Psychology'], 'skills': ['Visual design', 'Empathy for users', 'Prototyping tools (Figma)', 'Communication'], 'entrance_exams': ['UCEED', 'NID DAT', 'NIFT entrance'], 'education_pathway': 'Class 12 (any stream) -> B.Des. or a related degree -> internships building a design portfolio -> junior designer role.', 'roadmap': 'Explore: notice apps/websites you find easy or annoying to use, and ask why. Build: redesign a screen from an app you use, just as practice. Learn: pick up a free tool like Figma and follow a beginner tutorial. Apply: put 3-4 of your best practice projects in a simple portfolio site.'}, {'category_key': 'law', 'slug': 'lawyer', 'title': 'Lawyer (Advocate)', 'description': 'Lawyers advise people and organizations on legal matters and represent them in court, negotiations, or contracts — specializing over time in areas like criminal, corporate, or family law.', 'eligibility': "A 5-year integrated law degree (after Class 12) or a 3-year LLB (after any bachelor's degree), followed by enrolling with the Bar Council.", 'subjects': ['English', 'Political Science', 'History'], 'skills': ['Reading comprehension', 'Argumentation', 'Research', 'Public speaking'], 'entrance_exams': ['CLAT', 'AILET', 'LSAT India'], 'education_pathway': 'Class 12 (any stream) -> CLAT -> 5-year integrated law degree (B.A. LLB or similar) -> internships at law firms/with lawyers -> Bar Council exam -> practicing advocate.', 'roadmap': 'Explore: follow a few well-known court cases in the news and how they were argued. Build: join your school/college debate or moot court society. Learn: CLAT tests reasoning and English as much as legal knowledge — practice both. Apply: internships during law school are where you actually learn the practice.'}, {'category_key': 'commerce_ca', 'slug': 'chartered-accountant', 'title': 'Chartered Accountant (CA)', 'description': "Chartered Accountants handle auditing, taxation, and financial reporting for businesses — a respected, in-demand qualification in India's finance world.", 'eligibility': "Can start right after Class 12 via the CA Foundation route, or after a bachelor's degree via direct entry.", 'subjects': ['Mathematics/Accountancy', 'Economics', 'English'], 'skills': ['Numerical accuracy', 'Attention to detail', 'Ethics', 'Analytical thinking'], 'entrance_exams': ['CA Foundation', 'CA Intermediate', 'CA Final (all via ICAI)'], 'education_pathway': 'Class 12 (Commerce preferred) -> CA Foundation -> CA Intermediate -> Articleship (practical training, ~2 years) -> CA Final -> Chartered Accountant.', 'roadmap': 'Explore: read about what accountants and auditors actually do day to day. Build: get comfortable with basic bookkeeping concepts early. Learn: the CA path is long and exam-heavy — steady, consistent study matters more than cramming. Apply: articleship is where the real-world learning happens.'}, {'category_key': 'entrepreneurship', 'slug': 'startup-founder', 'title': 'Entrepreneur / Startup Founder', 'description': 'Founders identify a problem worth solving, build a product or service around it, and take on the risk of building a business from scratch — in any industry, not a single fixed path.', 'eligibility': 'No formal degree required, though many founders study business, engineering, or a field related to their eventual startup first.', 'subjects': ['Economics', 'Business Studies', 'Any technical subject relevant to the idea'], 'skills': ['Risk tolerance', 'Sales', 'Resourcefulness', 'Leadership'], 'entrance_exams': None, 'education_pathway': 'No single path — common ones include: a relevant degree -> work experience -> start a company; or a technical/business degree with a startup incubator/accelerator along the way.', 'roadmap': "Explore: notice problems around you that annoy you enough to want to fix them. Build: try a small project or side-hustle, even a tiny one, to learn what building something real actually takes. Learn: read about founders in a field you're curious about. Apply: entering a school/college business plan competition is a low-risk way to practice pitching an idea."}, {'category_key': 'skilled_vocational', 'slug': 'electrician', 'title': 'Electrician', 'description': 'Electricians install, maintain, and repair electrical systems in homes, offices, and factories — a hands-on, steadily in-demand trade with a clear certification path.', 'eligibility': 'Class 10 pass, followed by an ITI diploma in Electrician trade.', 'subjects': ['Science', 'Mathematics'], 'skills': ['Hands-on technical work', 'Problem-solving', 'Safety awareness', 'Precision'], 'entrance_exams': ['ITI admission (state-level, varies by institute)'], 'education_pathway': 'Class 10 -> ITI Electrician trade (1-2 years) -> apprenticeship -> licensed electrician, or further study toward a diploma/degree in Electrical Engineering.', 'roadmap': 'Explore: notice how wiring and electrical systems work around your own home. Build: basic, safe hands-on practice under supervision if you can access it. Learn: ITI courses are practical and job-focused — check which local institutes are well-regarded. Apply: an apprenticeship after ITI is where real skill develops.'}, {'category_key': 'other', 'slug': 'school-teacher', 'title': 'School Teacher', 'description': 'Teachers educate and guide students through a subject and, often, through growing up — a career with real day-to-day impact and, in India, strong, structured demand.', 'eligibility': "A bachelor's degree in the subject you want to teach, plus a B.Ed. (Bachelor of Education) — some states also require passing a teacher eligibility test.", 'subjects': ["Any subject you'd like to teach", 'Education/Psychology (for B.Ed.)'], 'skills': ['Communication', 'Patience', 'Subject mastery', 'Classroom management'], 'entrance_exams': ['CTET / State TET', 'B.Ed. entrance exams (university-specific)'], 'education_pathway': "Class 12 -> bachelor's degree in your subject -> B.Ed. (2 years) -> CTET/TET -> teaching position in a school.", 'roadmap': "Explore: notice which of your own teachers made a subject click for you, and why. Build: tutoring a younger student, even informally, is real practice. Learn: pick a subject you're genuinely strong in — that's what you'll teach. Apply: many B.Ed. programs include supervised teaching practice — that's where it gets real."}, {'category_key': 'other', 'slug': 'journalist', 'title': 'Journalist', 'description': 'Journalists research, verify, and report news and stories across print, TV, or digital media — informing the public and holding power accountable.', 'eligibility': "A bachelor's degree in Journalism/Mass Communication, English, or any subject paired with a journalism postgraduate diploma.", 'subjects': ['English', 'Political Science', 'History'], 'skills': ['Writing', 'Research', 'Interviewing', 'Fact-checking'], 'entrance_exams': ['IIMC entrance exam', 'University-specific mass comm entrances'], 'education_pathway': "Class 12 (any stream) -> bachelor's in Journalism/Mass Communication (or any degree + a PG diploma in journalism) -> internships at a publication -> reporter/journalist role.", 'roadmap': 'Explore: read a range of news sources and notice differences in how the same story gets covered. Build: start a blog, school newsletter, or social account covering something you care about. Learn: strong, clear writing is the core skill — practice it constantly. Apply: internships at local publications are the most common way in.'}, {'category_key': 'engineering', 'slug': 'mechanical-engineer', 'title': 'Mechanical Engineer', 'description': 'Mechanical engineers design, build, and maintain machines and mechanical systems — from engines and manufacturing equipment to robotics and HVAC systems.', 'eligibility': "A bachelor's degree in Mechanical Engineering (B.Tech/B.E.).", 'subjects': ['Mathematics', 'Physics', 'Chemistry'], 'skills': ['Technical design (CAD)', 'Problem-solving', 'Physics/mechanics intuition', 'Teamwork'], 'entrance_exams': ['JEE Main', 'JEE Advanced', 'State CETs'], 'education_pathway': 'Class 12 (Science, PCM) -> B.Tech/B.E. in Mechanical Engineering -> internships -> entry-level design/manufacturing/maintenance role.', 'roadmap': 'Explore: notice how everyday machines around you work. Build: simple hands-on projects (even basic model-building) build real intuition. Learn: a solid grip on physics and maths pays off across the whole degree. Apply: internships in manufacturing or design firms show what the day-to-day work is really like.'}, {'category_key': 'medicine', 'slug': 'nurse', 'title': 'Nurse', 'description': 'Nurses provide direct patient care, support doctors, and are often the constant presence a patient sees through treatment and recovery — in hospitals, clinics, and community health settings.', 'eligibility': 'A B.Sc. Nursing degree (4 years) or a GNM diploma (3 years) after Class 12 (Science preferred).', 'subjects': ['Biology', 'Chemistry', 'Physics'], 'skills': ['Compassion', 'Attention to detail', 'Calm under pressure', 'Communication'], 'entrance_exams': ['NEET (for many B.Sc. Nursing programs)', 'State nursing entrances'], 'education_pathway': 'Class 12 (Science) -> B.Sc. Nursing or GNM diploma -> registration with the State Nursing Council -> staff nurse role, with room to specialize (ICU, pediatric, etc.) over time.', 'roadmap': 'Explore: read about the different nursing specializations that exist. Build: volunteering at a local clinic or health camp, if possible, gives real exposure. Learn: biology is the core subject to be strong in. Apply: clinical postings during the degree are where hands-on skill is built.'}, {'category_key': 'technology_ai', 'slug': 'ai-ml-engineer', 'title': 'AI/ML Engineer', 'description': 'AI/ML engineers build systems that learn from data — recommendation engines, image and speech recognition, chatbots, and more — sitting at the intersection of software engineering and applied statistics.', 'eligibility': "A bachelor's degree in Computer Science, Data Science, Mathematics, or a related field; many roles also value strong self-taught skills and projects.", 'subjects': ['Mathematics', 'Computer Science', 'Statistics'], 'skills': ['Programming (Python)', 'Statistics/probability', 'Problem-solving', 'Curiosity'], 'entrance_exams': ['JEE Main', 'JEE Advanced', 'State CETs'], 'education_pathway': 'Class 12 (Science, PCM) -> B.Tech/B.Sc. in CS or a related field -> machine learning coursework and projects -> internships -> ML engineer/data scientist role.', 'roadmap': 'Explore: try a beginner-friendly guided ML tutorial online to see what the work actually involves. Build: a couple of small projects (even simple ones) teach more than reading theory alone. Learn: strong maths (especially probability and linear algebra) makes everything after it easier. Apply: many companies value a portfolio of projects as much as a degree.'}]

DASHBOARD_SECTIONS = [
    {
        "key": "welcome",
        "name": "Welcome",
        "description": "Profile summary and greeting.",
        "component_key": "welcome_summary",
    },
    {
        "key": "ai_assistant",
        "name": "Ask Career AI",
        "description": "Quick answers to career, education and skill questions.",
        "component_key": "ai_assistant_card",
    },
    {
        "key": "continue_learning",
        "name": "Continue Learning",
        "description": "Your in-progress courses and the next lesson in each.",
        "component_key": "continue_learning_card",
    },
    {
        "key": "recent_announcements",
        "name": "Recent Announcements",
        "description": "The latest announcements relevant to you.",
        "component_key": "recent_announcements_card",
    },
]

ALL_ROLES = ["student", "parent", "mentor", "school_admin", "admin"]
# (section_key, role, display_order) -- matches the original 0004/0013 seeding exactly
ROLE_SECTION_ROWS = (
    [("welcome", role, 0) for role in ALL_ROLES]
    + [("ai_assistant", role, 1) for role in ALL_ROLES]
    + [("continue_learning", "student", 2)]
    + [("recent_announcements", role, 3) for role in ALL_ROLES]
)


def upgrade() -> None:
    conn = op.get_bind()

    languages = sa.table(
        "languages",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("native_name", sa.String),
        sa.column("is_active", sa.Boolean),
    )
    conn.execute(
        pg_insert(languages).values(LANGUAGES).on_conflict_do_nothing(index_elements=["code"])
    )

    categories = sa.table(
        "career_categories",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("key", sa.String),
        sa.column("name", sa.String),
        sa.column("display_order", sa.Integer),
    )
    conn.execute(
        pg_insert(categories)
        .values(
            [
                {"id": uuid.uuid4(), "key": key, "name": name, "display_order": order}
                for key, name, order in CATEGORIES
            ]
        )
        .on_conflict_do_nothing(index_elements=["key"])
    )

    category_ids = {
        row[0]: row[1]
        for row in conn.execute(sa.text("SELECT key, id FROM career_categories")).fetchall()
    }

    careers = sa.table(
        "careers",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("category_id", postgresql.UUID(as_uuid=True)),
        sa.column("slug", sa.String),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
        sa.column("eligibility", sa.Text),
        sa.column("subjects", postgresql.ARRAY(sa.String)),
        sa.column("skills", postgresql.ARRAY(sa.String)),
        sa.column("entrance_exams", postgresql.ARRAY(sa.String)),
        sa.column("education_pathway", sa.Text),
        sa.column("roadmap", sa.Text),
    )
    all_careers = ORIGINAL_CAREERS + NEW_CAREERS
    conn.execute(
        pg_insert(careers)
        .values(
            [
                {
                    "id": uuid.uuid4(),
                    "category_id": category_ids[c["category_key"]],
                    "slug": c["slug"],
                    "title": c["title"],
                    "description": c["description"],
                    "eligibility": c["eligibility"],
                    "subjects": c["subjects"],
                    "skills": c["skills"],
                    "entrance_exams": c["entrance_exams"],
                    "education_pathway": c["education_pathway"],
                    "roadmap": c["roadmap"],
                }
                for c in all_careers
            ]
        )
        .on_conflict_do_nothing(index_elements=["slug"])
    )

    sections = sa.table(
        "dashboard_sections",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("key", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("component_key", sa.String),
    )
    conn.execute(
        pg_insert(sections)
        .values([{"id": uuid.uuid4(), **s} for s in DASHBOARD_SECTIONS])
        .on_conflict_do_nothing(index_elements=["key"])
    )

    section_ids = {
        row[0]: row[1]
        for row in conn.execute(sa.text("SELECT key, id FROM dashboard_sections")).fetchall()
    }

    role_sections = sa.table(
        "role_dashboard_sections",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("dashboard_section_id", postgresql.UUID(as_uuid=True)),
        sa.column("role", sa.String),
        sa.column("enabled", sa.Boolean),
        sa.column("display_order", sa.Integer),
    )
    conn.execute(
        pg_insert(role_sections)
        .values(
            [
                {
                    "id": uuid.uuid4(),
                    "dashboard_section_id": section_ids[key],
                    "role": role,
                    "enabled": True,
                    "display_order": order,
                }
                for key, role, order in ROLE_SECTION_ROWS
            ]
        )
        .on_conflict_do_nothing(index_elements=["dashboard_section_id", "role"])
    )


def downgrade() -> None:
    # Deliberately a no-op: this migration only ever ADDS rows that
    # were missing (ON CONFLICT DO NOTHING), it never removes or
    # modifies anything that was already there. There is nothing safe
    # to "undo" -- removing these rows again would just reproduce the
    # exact data-loss state this migration exists to repair.
    pass
