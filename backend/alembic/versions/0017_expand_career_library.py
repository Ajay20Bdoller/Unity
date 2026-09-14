"""expand career library: 12 more careers

Revision ID: 0017
Revises: 0016
Create Date: 2026-09-14

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None

CATEGORY_KEYS = [
    "engineering", "medicine", "upsc", "defence", "research_science",
    "technology_ai", "design", "law", "commerce_ca", "entrepreneurship",
    "skilled_vocational", "other",
]

NEW_CAREERS = [
    {
        "category_key": "defence",
        "slug": "army-officer",
        "title": "Army Officer",
        "description": (
            "Officers lead soldiers and manage operations in the Indian Army — a mix of "
            "leadership, discipline, and technical roles across infantry, engineering, "
            "medical, and other branches."
        ),
        "eligibility": "After Class 12 via NDA, or after a bachelor's degree via CDS — age "
        "and physical fitness criteria apply.",
        "subjects": ["Mathematics", "Physics", "English"],
        "skills": ["Leadership", "Physical fitness", "Decision-making under pressure", "Teamwork"],
        "entrance_exams": ["NDA", "CDS", "SSB Interview"],
        "education_pathway": "Class 12 -> NDA written exam + SSB interview -> National "
        "Defence Academy (3 years) -> Indian Military Academy -> commissioned officer. "
        "(Or: bachelor's degree -> CDS -> IMA/OTA.)",
        "roadmap": "Explore: read about the different Army branches (infantry, engineers, "
        "signals, medical). Build: work on physical fitness early — the SSB tests both mind "
        "and body. Learn: NDA exam covers maths, English, and general knowledge. Apply: "
        "practice previous years' NDA papers and mock SSB interviews.",
    },
    {
        "category_key": "research_science",
        "slug": "research-scientist",
        "title": "Research Scientist",
        "description": (
            "Research scientists investigate open questions in a field — designing "
            "experiments, analyzing data, and publishing findings that push knowledge "
            "forward, in universities, government labs, or industry R&D."
        ),
        "eligibility": "Bachelor's degree in a science field, followed by a master's and "
        "usually a PhD for independent research roles.",
        "subjects": ["Physics", "Chemistry", "Biology", "Mathematics"],
        "skills": ["Curiosity", "Patience", "Data analysis", "Scientific writing"],
        "entrance_exams": ["JEE/NEET (for the bachelor's degree)", "CSIR-NET", "GATE", "JEST"],
        "education_pathway": "Class 12 (Science) -> B.Sc. in a chosen subject -> M.Sc. -> "
        "PhD (often funded, with a stipend) -> postdoctoral research -> scientist/faculty "
        "position.",
        "roadmap": "Explore: read popular science writing in an area that interests you. "
        "Build: try a school or college science fair project. Learn: a strong foundation in "
        "one subject matters more than breadth early on. Apply: summer research internships "
        "(many institutes run them) are the best way to see if research suits you.",
    },
    {
        "category_key": "design",
        "slug": "ux-ui-designer",
        "title": "UX/UI Designer",
        "description": (
            "UX/UI designers shape how apps and websites look and feel — researching what "
            "users need, sketching layouts, and testing whether the result is actually easy "
            "to use."
        ),
        "eligibility": "A design degree helps but isn't mandatory — many designers build a "
        "portfolio through self-study, bootcamps, or a related degree (like Computer Science "
        "or Psychology) plus design courses.",
        "subjects": ["Art/Design", "Computer Science", "Psychology"],
        "skills": ["Visual design", "Empathy for users", "Prototyping tools (Figma)", "Communication"],
        "entrance_exams": ["UCEED", "NID DAT", "NIFT entrance"],
        "education_pathway": "Class 12 (any stream) -> B.Des. or a related degree -> "
        "internships building a design portfolio -> junior designer role.",
        "roadmap": "Explore: notice apps/websites you find easy or annoying to use, and ask "
        "why. Build: redesign a screen from an app you use, just as practice. Learn: pick up "
        "a free tool like Figma and follow a beginner tutorial. Apply: put 3-4 of your best "
        "practice projects in a simple portfolio site.",
    },
    {
        "category_key": "law",
        "slug": "lawyer",
        "title": "Lawyer (Advocate)",
        "description": (
            "Lawyers advise people and organizations on legal matters and represent them in "
            "court, negotiations, or contracts — specializing over time in areas like "
            "criminal, corporate, or family law."
        ),
        "eligibility": "A 5-year integrated law degree (after Class 12) or a 3-year LLB "
        "(after any bachelor's degree), followed by enrolling with the Bar Council.",
        "subjects": ["English", "Political Science", "History"],
        "skills": ["Reading comprehension", "Argumentation", "Research", "Public speaking"],
        "entrance_exams": ["CLAT", "AILET", "LSAT India"],
        "education_pathway": "Class 12 (any stream) -> CLAT -> 5-year integrated law degree "
        "(B.A. LLB or similar) -> internships at law firms/with lawyers -> Bar Council exam "
        "-> practicing advocate.",
        "roadmap": "Explore: follow a few well-known court cases in the news and how they "
        "were argued. Build: join your school/college debate or moot court society. Learn: "
        "CLAT tests reasoning and English as much as legal knowledge — practice both. Apply: "
        "internships during law school are where you actually learn the practice.",
    },
    {
        "category_key": "commerce_ca",
        "slug": "chartered-accountant",
        "title": "Chartered Accountant (CA)",
        "description": (
            "Chartered Accountants handle auditing, taxation, and financial reporting for "
            "businesses — a respected, in-demand qualification in India's finance world."
        ),
        "eligibility": "Can start right after Class 12 via the CA Foundation route, or after "
        "a bachelor's degree via direct entry.",
        "subjects": ["Mathematics/Accountancy", "Economics", "English"],
        "skills": ["Numerical accuracy", "Attention to detail", "Ethics", "Analytical thinking"],
        "entrance_exams": ["CA Foundation", "CA Intermediate", "CA Final (all via ICAI)"],
        "education_pathway": "Class 12 (Commerce preferred) -> CA Foundation -> CA "
        "Intermediate -> Articleship (practical training, ~2 years) -> CA Final -> "
        "Chartered Accountant.",
        "roadmap": "Explore: read about what accountants and auditors actually do day to "
        "day. Build: get comfortable with basic bookkeeping concepts early. Learn: the CA "
        "path is long and exam-heavy — steady, consistent study matters more than cramming. "
        "Apply: articleship is where the real-world learning happens.",
    },
    {
        "category_key": "entrepreneurship",
        "slug": "startup-founder",
        "title": "Entrepreneur / Startup Founder",
        "description": (
            "Founders identify a problem worth solving, build a product or service around "
            "it, and take on the risk of building a business from scratch — in any "
            "industry, not a single fixed path."
        ),
        "eligibility": "No formal degree required, though many founders study business, "
        "engineering, or a field related to their eventual startup first.",
        "subjects": ["Economics", "Business Studies", "Any technical subject relevant to the idea"],
        "skills": ["Risk tolerance", "Sales", "Resourcefulness", "Leadership"],
        "entrance_exams": None,
        "education_pathway": "No single path — common ones include: a relevant degree -> "
        "work experience -> start a company; or a technical/business degree with a startup "
        "incubator/accelerator along the way.",
        "roadmap": "Explore: notice problems around you that annoy you enough to want to fix "
        "them. Build: try a small project or side-hustle, even a tiny one, to learn what "
        "building something real actually takes. Learn: read about founders in a field "
        "you're curious about. Apply: entering a school/college business plan competition is "
        "a low-risk way to practice pitching an idea.",
    },
    {
        "category_key": "skilled_vocational",
        "slug": "electrician",
        "title": "Electrician",
        "description": (
            "Electricians install, maintain, and repair electrical systems in homes, "
            "offices, and factories — a hands-on, steadily in-demand trade with a clear "
            "certification path."
        ),
        "eligibility": "Class 10 pass, followed by an ITI diploma in Electrician trade.",
        "subjects": ["Science", "Mathematics"],
        "skills": ["Hands-on technical work", "Problem-solving", "Safety awareness", "Precision"],
        "entrance_exams": ["ITI admission (state-level, varies by institute)"],
        "education_pathway": "Class 10 -> ITI Electrician trade (1-2 years) -> apprenticeship "
        "-> licensed electrician, or further study toward a diploma/degree in Electrical "
        "Engineering.",
        "roadmap": "Explore: notice how wiring and electrical systems work around your own "
        "home. Build: basic, safe hands-on practice under supervision if you can access it. "
        "Learn: ITI courses are practical and job-focused — check which local institutes are "
        "well-regarded. Apply: an apprenticeship after ITI is where real skill develops.",
    },
    {
        "category_key": "other",
        "slug": "school-teacher",
        "title": "School Teacher",
        "description": (
            "Teachers educate and guide students through a subject and, often, through "
            "growing up — a career with real day-to-day impact and, in India, strong, "
            "structured demand."
        ),
        "eligibility": "A bachelor's degree in the subject you want to teach, plus a B.Ed. "
        "(Bachelor of Education) — some states also require passing a teacher eligibility "
        "test.",
        "subjects": ["Any subject you'd like to teach", "Education/Psychology (for B.Ed.)"],
        "skills": ["Communication", "Patience", "Subject mastery", "Classroom management"],
        "entrance_exams": ["CTET / State TET", "B.Ed. entrance exams (university-specific)"],
        "education_pathway": "Class 12 -> bachelor's degree in your subject -> B.Ed. (2 "
        "years) -> CTET/TET -> teaching position in a school.",
        "roadmap": "Explore: notice which of your own teachers made a subject click for "
        "you, and why. Build: tutoring a younger student, even informally, is real practice. "
        "Learn: pick a subject you're genuinely strong in — that's what you'll teach. Apply: "
        "many B.Ed. programs include supervised teaching practice — that's where it gets "
        "real.",
    },
    {
        "category_key": "other",
        "slug": "journalist",
        "title": "Journalist",
        "description": (
            "Journalists research, verify, and report news and stories across print, TV, "
            "or digital media — informing the public and holding power accountable."
        ),
        "eligibility": "A bachelor's degree in Journalism/Mass Communication, English, or "
        "any subject paired with a journalism postgraduate diploma.",
        "subjects": ["English", "Political Science", "History"],
        "skills": ["Writing", "Research", "Interviewing", "Fact-checking"],
        "entrance_exams": ["IIMC entrance exam", "University-specific mass comm entrances"],
        "education_pathway": "Class 12 (any stream) -> bachelor's in Journalism/Mass "
        "Communication (or any degree + a PG diploma in journalism) -> internships at a "
        "publication -> reporter/journalist role.",
        "roadmap": "Explore: read a range of news sources and notice differences in how the "
        "same story gets covered. Build: start a blog, school newsletter, or social account "
        "covering something you care about. Learn: strong, clear writing is the core skill — "
        "practice it constantly. Apply: internships at local publications are the most "
        "common way in.",
    },
    {
        "category_key": "engineering",
        "slug": "mechanical-engineer",
        "title": "Mechanical Engineer",
        "description": (
            "Mechanical engineers design, build, and maintain machines and mechanical "
            "systems — from engines and manufacturing equipment to robotics and HVAC "
            "systems."
        ),
        "eligibility": "A bachelor's degree in Mechanical Engineering (B.Tech/B.E.).",
        "subjects": ["Mathematics", "Physics", "Chemistry"],
        "skills": ["Technical design (CAD)", "Problem-solving", "Physics/mechanics intuition", "Teamwork"],
        "entrance_exams": ["JEE Main", "JEE Advanced", "State CETs"],
        "education_pathway": "Class 12 (Science, PCM) -> B.Tech/B.E. in Mechanical "
        "Engineering -> internships -> entry-level design/manufacturing/maintenance role.",
        "roadmap": "Explore: notice how everyday machines around you work. Build: simple "
        "hands-on projects (even basic model-building) build real intuition. Learn: a solid "
        "grip on physics and maths pays off across the whole degree. Apply: internships in "
        "manufacturing or design firms show what the day-to-day work is really like.",
    },
    {
        "category_key": "medicine",
        "slug": "nurse",
        "title": "Nurse",
        "description": (
            "Nurses provide direct patient care, support doctors, and are often the "
            "constant presence a patient sees through treatment and recovery — in "
            "hospitals, clinics, and community health settings."
        ),
        "eligibility": "A B.Sc. Nursing degree (4 years) or a GNM diploma (3 years) after "
        "Class 12 (Science preferred).",
        "subjects": ["Biology", "Chemistry", "Physics"],
        "skills": ["Compassion", "Attention to detail", "Calm under pressure", "Communication"],
        "entrance_exams": ["NEET (for many B.Sc. Nursing programs)", "State nursing entrances"],
        "education_pathway": "Class 12 (Science) -> B.Sc. Nursing or GNM diploma -> "
        "registration with the State Nursing Council -> staff nurse role, with room to "
        "specialize (ICU, pediatric, etc.) over time.",
        "roadmap": "Explore: read about the different nursing specializations that exist. "
        "Build: volunteering at a local clinic or health camp, if possible, gives real "
        "exposure. Learn: biology is the core subject to be strong in. Apply: clinical "
        "postings during the degree are where hands-on skill is built.",
    },
    {
        "category_key": "technology_ai",
        "slug": "ai-ml-engineer",
        "title": "AI/ML Engineer",
        "description": (
            "AI/ML engineers build systems that learn from data — recommendation engines, "
            "image and speech recognition, chatbots, and more — sitting at the intersection "
            "of software engineering and applied statistics."
        ),
        "eligibility": "A bachelor's degree in Computer Science, Data Science, Mathematics, "
        "or a related field; many roles also value strong self-taught skills and projects.",
        "subjects": ["Mathematics", "Computer Science", "Statistics"],
        "skills": ["Programming (Python)", "Statistics/probability", "Problem-solving", "Curiosity"],
        "entrance_exams": ["JEE Main", "JEE Advanced", "State CETs"],
        "education_pathway": "Class 12 (Science, PCM) -> B.Tech/B.Sc. in CS or a related "
        "field -> machine learning coursework and projects -> internships -> ML "
        "engineer/data scientist role.",
        "roadmap": "Explore: try a beginner-friendly guided ML tutorial online to see what "
        "the work actually involves. Build: a couple of small projects (even simple ones) "
        "teach more than reading theory alone. Learn: strong maths (especially probability "
        "and linear algebra) makes everything after it easier. Apply: many companies value a "
        "portfolio of projects as much as a degree.",
    },
]


def upgrade() -> None:
    conn = op.get_bind()
    category_rows = conn.execute(
        sa.text("SELECT id, key FROM career_categories WHERE key = ANY(:keys)"),
        {"keys": CATEGORY_KEYS},
    ).fetchall()
    category_ids = {key: id_ for id_, key in category_rows}

    career_table = sa.table(
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

    op.bulk_insert(
        career_table,
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
            for c in NEW_CAREERS
        ],
    )


def downgrade() -> None:
    slugs = [c["slug"] for c in NEW_CAREERS]
    placeholders = "', '".join(slugs)
    op.execute(f"DELETE FROM careers WHERE slug IN ('{placeholders}')")
