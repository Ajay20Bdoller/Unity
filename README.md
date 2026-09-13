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

## Testing

```bash
cd backend && pip install -r requirements-dev.txt && pytest
cd frontend && npx tsc --noEmit && npm run lint
```

## Conventions & roadmap

See [`CLAUDE.md`](./CLAUDE.md) for architecture rules, coding conventions,
security/database rules, and the full phased build plan.

## Status

- [x] JWT auth: register / login / refresh (rotating, revocable,
      frontend auto-retries on 401) / logout / me
- [x] Roles: STUDENT, PARENT, MENTOR, SCHOOL_ADMIN, ADMIN (ADMIN not
      self-registerable) with `require_*` authorization dependencies
- [x] Identity/role-profile split: `users` + `students`/`parents`/
      `mentors`/`school_admin_profiles`
- [x] `languages` table (seeded) + `PATCH /users/me/language`
- [x] `states`/`districts`/`schools` tables (schema only, no data yet)
- [x] Student onboarding, guardian relationships, per-feature consent
      (dev-mode OTP)
- [x] Dashboard config backend + registry-driven frontend rendering
- [x] AI Career Assistant (backend + dashboard card) — needs a real
      `GROK_API_KEY` to actually answer (see CLAUDE.md §11)
- [x] Career library (categories, careers, translations, related
      careers, student interests) — backend only, no frontend UI yet
- [x] Courses, modules, lessons (video/article/quiz/external),
      enrollment, lesson progress, continue-learning — backend only
- [ ] Assessment, campaigns, mentorship, announcements, admin APIs/UI,
      i18n

See [`CLAUDE.md`](./CLAUDE.md) §11 for the full phased plan.
