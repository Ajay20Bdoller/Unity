"""expand course library further: 12 more courses (15+ total)

Revision ID: 0023
Revises: 0022
Create Date: 2026-10-02

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None

# Each: (slug, title, description, [(module_title, [(lesson_title, body_or_(url,))])])
COURSES = [
    (
        "exploring-engineering-careers",
        "Exploring Engineering Careers",
        "A first look at what engineers actually do day to day, across the major branches.",
        [
            ("What engineers do", [
                ("Not just one job", "\"Engineer\" covers very different day-to-day work: a civil engineer might spend the morning on a construction site, a software engineer debugging code, a mechanical engineer reviewing a design in CAD. What they share is turning a real-world problem into a working solution within real constraints -- cost, safety, time."),
                ("The major branches, briefly", "Civil (buildings, roads, water systems), Mechanical (machines, engines, manufacturing), Electrical (power, circuits, electronics), Computer Science (software, systems), Chemical (industrial processes, materials). Most other branches are combinations or specializations of these."),
            ]),
            ("Is it for you", [
                ("A realistic self-check", "You don't need to already love maths and physics to try engineering, but you do need to be willing to get comfortable with them -- they're the shared language across every branch. More telling: do you enjoy figuring out *why* something works, not just *that* it works?"),
            ]),
        ],
    ),
    (
        "medicine-healthcare-careers",
        "Medicine & Healthcare Careers: A First Look",
        "An honest look at what a career in medicine actually involves -- the demands, the timeline, and the many roles beyond \"doctor.\"",
        [
            ("Beyond \"doctor\"", [
                ("More roles than you might think", "Healthcare needs doctors, but also nurses, pharmacists, physiotherapists, lab technicians, public health researchers, and hospital administrators. Each has a different training path, timeline, and day-to-day reality -- worth knowing before assuming MBBS is the only route in."),
                ("The real timeline", "MBBS is roughly 5.5 years (including an internship), then often further years of specialization if you want to practice a specific field. This is one of the longest common education paths -- a realistic, not discouraging, thing to know early."),
            ]),
            ("What the work is actually like", [
                ("The parts people don't always mention", "Long hours, emotionally difficult days, and years of continued study even after qualifying are real parts of the job -- alongside the parts people usually highlight. Worth sitting with both before committing years of preparation toward NEET."),
            ]),
        ],
    ),
    (
        "law-as-a-career",
        "Law as a Career: Getting Started",
        "What lawyers actually do, the different paths within law, and how to start preparing.",
        [
            ("What lawyers actually do", [
                ("Litigation vs. everything else", "Courtroom litigation is the most visible kind of legal work, but far from the only one -- corporate lawyers draft contracts and advise businesses, many lawyers never see a courtroom at all. Worth knowing before assuming \"lawyer\" means one thing."),
                ("Reading is most of the job", "Whatever the specialty, a huge share of legal work is reading closely -- contracts, case law, statutes -- and writing clearly about what you found. If that sounds tedious rather than interesting, it's worth sitting with that honestly."),
            ]),
            ("Starting to prepare", [
                ("CLAT, in plain terms", "CLAT (Common Law Admission Test) tests English comprehension, general knowledge, legal reasoning, logical reasoning, and maths -- less about knowing law already, more about reasoning and reading carefully under time pressure."),
            ]),
        ],
    ),
    (
        "commerce-ca-basics",
        "Commerce & Chartered Accountancy Basics",
        "An introduction to commerce as a stream and what the CA path actually involves.",
        [
            ("Why commerce, and what it leads to", [
                ("More than \"good with numbers\"", "Commerce covers accounting, economics, business studies, and more -- it leads to many paths beyond CA: banking, finance, business management, entrepreneurship. Being comfortable with numbers helps, but curiosity about how businesses and money actually work matters more."),
            ]),
            ("The CA path, honestly", [
                ("A long, exam-heavy road", "CA Foundation, then Intermediate, then roughly two years of practical Articleship training, then CA Final -- each stage has real exams with real failure rates. It rewards consistent, steady study far more than last-minute effort."),
                ("What Articleship actually teaches", "The two years of practical training under a practicing CA is where most real learning happens -- auditing real company accounts, preparing real tax filings. The exams test knowledge; Articleship is where it becomes a skill."),
            ]),
        ],
    ),
    (
        "entrepreneurship-fundamentals",
        "Entrepreneurship Fundamentals",
        "The basics of starting something of your own -- what it actually takes, beyond the idea.",
        [
            ("It starts with a problem, not an idea", [
                ("Problem first, product second", "The strongest starting point isn't \"I have a cool idea\" but \"I keep noticing this problem, and nobody's solved it well.\" An idea without a real problem behind it usually struggles to find anyone who actually wants it."),
            ]),
            ("What founders actually spend time on", [
                ("Less glamorous than it looks from outside", "Much of early-stage founder time goes to unglamorous things: talking to potential customers, fixing small operational problems, figuring out how to pay for things. The exciting \"building the big vision\" part is real, but it's a smaller share of the time than most expect."),
                ("Risk is real, not just a buzzword", "Most new ventures don't succeed on the first try -- that's a normal, not shameful, part of how this path works. Worth going in with eyes open about that rather than assuming the risk is smaller than it is."),
            ]),
        ],
    ),
    (
        "intro-to-ux-ui-design",
        "Introduction to UX/UI Design",
        "What UX/UI designers actually do, and a first taste of thinking like one.",
        [
            ("UX vs UI, simply", [
                ("Two related but different jobs", "UI (user interface) is how something looks -- colors, layout, buttons. UX (user experience) is how it *works* for the person using it -- is it confusing, is it fast, does it do what they expected? Good design needs both."),
            ]),
            ("Thinking like a designer", [
                ("Notice friction", "Next time an app or website frustrates you, pause and ask why -- too many steps, unclear labels, a button that's hard to find. That habit of noticing friction, and asking what would fix it, is most of what the job trains."),
                ("A tiny first exercise", "Pick a screen from an app you use daily. Sketch (even on paper) one small change that would make it clearer or faster. That's literally the core loop of the job, just without a client yet."),
            ]),
        ],
    ),
    (
        "public-speaking-basics",
        "Public Speaking Basics",
        "Practical ways to get more comfortable and clear speaking in front of others -- useful in any career.",
        [
            ("Why it's worth building this skill", [
                ("It shows up everywhere", "Interviews, class presentations, team meetings, pitching an idea -- clear speaking under a bit of pressure matters across every career, not just \"public speaking\" jobs. It's also a skill that genuinely improves with practice, not a fixed trait."),
            ]),
            ("Simple habits that help", [
                ("Structure beats memorization", "Trying to memorize a speech word-for-word often makes nervousness worse -- if you forget one word, you can freeze. Instead, know your 3-4 main points cold, and let the exact words come naturally each time."),
                ("Practice out loud, not just in your head", "Reading your points silently feels very different from saying them out loud. Practice to a mirror, a friend, or your phone's voice recorder -- hearing yourself is how the nervousness wears off."),
            ]),
        ],
    ),
    (
        "personal-finance-for-students",
        "Personal Finance for Students",
        "The basics of managing money well -- habits worth starting young, long before a full-time salary.",
        [
            ("Why start now", [
                ("Habits are easier to build early", "The habit of tracking where money goes, and the comfort with budgeting, are much easier to build with small amounts of pocket money than to learn for the first time once a real salary and real bills show up."),
            ]),
            ("A few core ideas", [
                ("Spending vs. saving vs. giving", "A simple, durable habit: whenever money comes in, decide upfront roughly how much is for spending now, how much for saving toward something, and (if you choose) how much to give. Deciding in advance beats deciding in the moment."),
                ("What compounding actually means", "Money saved and invested early grows faster over time than the same amount saved later, because it earns returns on its returns, compounding year after year. It's one of the few places where starting early matters more than starting with more."),
            ]),
        ],
    ),
    (
        "time-management-for-students",
        "Time Management for Students",
        "Practical, realistic habits for managing schoolwork, exam prep, and everything else competing for your time.",
        [
            ("Why most time-management advice fails", [
                ("Plans that ignore real life don't survive contact with it", "A perfect-looking schedule that assumes you'll feel focused for 6 straight hours rarely survives the first tiring day. Realistic plans build in rest, interruptions, and some slack -- they're more likely to actually get followed."),
            ]),
            ("A few practical techniques", [
                ("Do the hardest thing first", "Energy and willpower are usually highest earlier in a work session. Starting with the task you're most tempted to avoid, while you still have that energy, beats saving it for last when you're tired and low on willpower."),
                ("Write it down, don't just remember it", "Holding a mental list of everything you need to do takes real mental energy and causes background stress. Writing tasks down -- even a simple paper list -- frees up that energy for the actual work."),
            ]),
        ],
    ),
    (
        "exam-preparation-strategies",
        "Exam Preparation Strategies",
        "Study techniques that actually work, backed by how memory and learning really function.",
        [
            ("Why re-reading notes doesn't work well", [
                ("Familiar isn't the same as learned", "Re-reading notes feels productive because the material starts to feel familiar -- but familiarity is a weak predictor of whether you can actually recall it under exam pressure, without the notes in front of you."),
            ]),
            ("What works better", [
                ("Active recall", "Instead of re-reading, close the book and try to write down or say everything you remember about a topic, then check what you missed. This feels harder in the moment -- that difficulty is exactly what makes it more effective."),
                ("Spacing it out", "Studying a topic once, then again a few days later, then again a week after that, builds much stronger long-term memory than the same total hours crammed into one sitting right before the exam."),
            ]),
        ],
    ),
    (
        "building-your-first-resume",
        "Building Your First Resume",
        "How to put together a first resume, even with little or no work experience yet.",
        [
            ("You have more to put on it than you think", [
                ("Experience isn't only jobs", "School projects, competitions, volunteering, a club you helped run, something you built or organized -- all of this counts as real experience worth including, especially for a first resume."),
            ]),
            ("Making it clear and honest", [
                ("Be specific, not vague", "\"Helped organize an event\" says little. \"Coordinated logistics for a 100-person school event, managing a 5-person volunteer team\" says a lot more, and is more convincing -- as long as it's accurate."),
                ("Keep it honest", "It's tempting to stretch a small role into a bigger-sounding one. Resist that -- a specific, honest, smaller claim holds up far better in an interview than an exaggerated one that falls apart under a simple follow-up question."),
            ]),
        ],
    ),
    (
        "intro-to-civil-services",
        "Introduction to Civil Services (UPSC)",
        "What a career in the civil services actually looks like, and what the exam process involves.",
        [
            ("What civil servants actually do", [
                ("Real administrative power and responsibility", "IAS, IPS, and IFS officers run districts, oversee law and order, implement government policy on the ground, and represent India abroad -- genuinely high-responsibility, high-impact roles, not just prestigious titles."),
            ]),
            ("The exam, honestly", [
                ("Three stages, a long road", "Preliminary (objective), Mains (written, several papers), and an Interview -- most successful candidates prepare for well over a year, often while balancing other work or studies. It's a serious, multi-year commitment, not a quick exam to clear."),
            ]),
        ],
    ),
]


def upgrade() -> None:
    courses_table = sa.table(
        "courses",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("slug", sa.String),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
        sa.column("published", sa.Boolean),
    )
    modules_table = sa.table(
        "modules",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("course_id", postgresql.UUID(as_uuid=True)),
        sa.column("title", sa.String),
        sa.column("display_order", sa.Integer),
    )
    lessons_table = sa.table(
        "lessons",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("module_id", postgresql.UUID(as_uuid=True)),
        sa.column("title", sa.String),
        sa.column("content_type", sa.String),
        sa.column("content_url", sa.String),
        sa.column("content_body", sa.Text),
        sa.column("display_order", sa.Integer),
    )

    course_rows = []
    module_rows = []
    lesson_rows = []

    for slug, title, description, modules in COURSES:
        course_id = uuid.uuid4()
        course_rows.append(
            {
                "id": course_id,
                "slug": slug,
                "title": title,
                "description": description,
                "published": True,
            }
        )
        for m_order, (m_title, lessons) in enumerate(modules):
            module_id = uuid.uuid4()
            module_rows.append(
                {
                    "id": module_id,
                    "course_id": course_id,
                    "title": m_title,
                    "display_order": m_order,
                }
            )
            for l_order, (l_title, l_body) in enumerate(lessons):
                lesson_rows.append(
                    {
                        "id": uuid.uuid4(),
                        "module_id": module_id,
                        "title": l_title,
                        "content_type": "article",
                        "content_url": None,
                        "content_body": l_body,
                        "display_order": l_order,
                    }
                )

    op.bulk_insert(courses_table, course_rows)
    op.bulk_insert(modules_table, module_rows)
    op.bulk_insert(lessons_table, lesson_rows)


def downgrade() -> None:
    slugs = [c[0] for c in COURSES]
    placeholders = "', '".join(slugs)
    op.execute(
        f"DELETE FROM lessons WHERE module_id IN "
        f"(SELECT id FROM modules WHERE course_id IN "
        f"(SELECT id FROM courses WHERE slug IN ('{placeholders}')))"
    )
    op.execute(
        f"DELETE FROM modules WHERE course_id IN "
        f"(SELECT id FROM courses WHERE slug IN ('{placeholders}'))"
    )
    op.execute(f"DELETE FROM courses WHERE slug IN ('{placeholders}')")
