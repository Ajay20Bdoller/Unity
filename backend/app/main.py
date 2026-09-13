from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    ai,
    assessments,
    auth,
    campaigns,
    careers,
    courses,
    dashboard,
    health,
    parents,
    students,
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

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(students.router)
app.include_router(parents.router)
app.include_router(dashboard.router)
app.include_router(dashboard.admin_router)
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
