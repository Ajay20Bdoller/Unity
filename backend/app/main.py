from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    admin_consent,
    admin_stats,
    admin_users,
    ai,
    announcements,
    assessments,
    auth,
    campaigns,
    careers,
    courses,
    dashboard,
    languages,
    health,
    locations,
    mentorship,
    parents,
    schools,
    students,
    team,
    users,
)
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="Unity Career Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Standard, low-risk response headers that were missing entirely —
    none of these change behavior for this app's own frontend, they
    only add defense-in-depth against things like clickjacking and
    MIME-sniffing for anyone else who might ever load an API response
    directly (e.g. an error page) in a browser."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.ENVIRONMENT != "development":
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(students.router)
app.include_router(parents.router)
app.include_router(dashboard.router)
app.include_router(dashboard.admin_router)
app.include_router(dashboard.message_admin_router)
app.include_router(ai.router)
app.include_router(careers.router)
app.include_router(careers.student_router)
app.include_router(careers.admin_router)
app.include_router(courses.router)
app.include_router(courses.student_router)
app.include_router(courses.admin_router)
app.include_router(campaigns.router)
app.include_router(assessments.router)
app.include_router(assessments.student_router)
app.include_router(assessments.admin_router)
app.include_router(mentorship.router)
app.include_router(mentorship.mentor_router)
app.include_router(mentorship.student_router)
app.include_router(mentorship.session_router)
app.include_router(mentorship.admin_router)
app.include_router(announcements.router)
app.include_router(announcements.admin_router)
app.include_router(languages.router)
app.include_router(schools.router)
app.include_router(locations.router)
app.include_router(team.router)
app.include_router(team.admin_router)
app.include_router(admin_users.router)
app.include_router(admin_stats.router)
app.include_router(admin_consent.router)
