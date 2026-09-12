# Unity — Career Guidance Platform

A career-awareness, guidance, learning and mentorship platform for school
students in India, with a focus on rural and underserved communities.

## Stack

- **Frontend:** Next.js (App Router) + TypeScript + Tailwind CSS
- **Backend:** FastAPI + SQLAlchemy 2.x + Alembic + PostgreSQL (Neon)
- **AI:** Grok API, called only from the backend (never from the frontend)

## Structure

```
backend/   FastAPI app, SQLAlchemy models, Alembic migrations
frontend/  Next.js app
```

## Backend setup

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in DATABASE_URL, JWT_SECRET_KEY, GROK_API_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

## Frontend setup

```bash
cd frontend
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL
npm run dev
```

## Status (Phase 1 — Foundation)

- [x] JWT auth: register / login / logout / me
- [x] User model with 5 roles (student, parent, mentor, school, admin)
- [x] Alembic migration for `users` table
- [x] Next.js skeleton with login/register/dashboard wired to the API
- [ ] AI Career Assistant (Phase 2)
- [ ] Onboarding, career library, assessment (Phase 3+)

See project roadmap for the full phased plan.
