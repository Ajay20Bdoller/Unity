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

## First admin account

ADMIN can't self-register (see CLAUDE.md §5). Create one with:
```bash
cd backend && python -m scripts.create_admin --email you@example.com --name "Your Name"
```

## Testing

```bash
cd backend && pip install -r requirements-dev.txt && pytest
cd frontend && npx tsc --noEmit && npm run lint
```

## Conventions & roadmap

See [`CLAUDE.md`](./CLAUDE.md) for architecture rules, coding conventions,
security/database rules, and the full phased build plan.

## Status

Backend: auth (login by email or mobile), role-specific registration
validation, onboarding, guardian/consent, dashboard config, AI
assistant, career library, courses, campaigns, assessment, mentorship,
announcements, admin APIs. Frontend: role-specific registration form,
dark/light mode, language switcher, full app + admin UI. See
[`CLAUDE.md`](./CLAUDE.md) §11 for full detail and honest gaps.
