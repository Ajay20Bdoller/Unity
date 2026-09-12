# CLAUDE.md

Source of truth for any Claude / Claude Code session working on this repo.
Read this before making architectural decisions. Keep it updated as the
project evolves — stale docs are worse than no docs.

## 1. Project purpose

**Unity** — a career-awareness, guidance, learning and mentorship platform
for school students in India, with a focus on rural and underserved
communities. It should feel like a **personal career companion**, not a
generic course marketplace.

Core journey: **Discover → Understand → Explore → Assess → Learn →
Get Guidance → Track Progress**.

Five roles, all first-class: **Student, Parent/Guardian, Mentor,
School/Institution, Admin.** The AI Career Assistant is available to
every authenticated role, not just students.

## 2. Architecture

```
Next.js (frontend)
   │  REST/JSON, JWT in httpOnly cookie
   ▼
FastAPI (backend)
   │  SQLAlchemy
   ▼
Neon PostgreSQL

FastAPI ──▶ Grok API   (AI Career Assistant; backend-only, never from frontend)
```

Hard rule: the frontend **never** talks to Postgres or Grok directly.
Everything goes through the FastAPI REST API.

## 3. Tech stack

- **Frontend:** Next.js (App Router) 15.5.x, TypeScript (strict), Tailwind
  CSS, custom lightweight UI components (`frontend/components/ui/`) —
  shadcn/ui not yet pulled in, current components follow its conventions
  so migrating later is low-friction.
- **Backend:** FastAPI, Pydantic v2, SQLAlchemy 2.x (typed `Mapped[...]`
  style), Alembic, `python-jose` for JWT, `passlib[bcrypt]` for hashing.
- **DB:** Neon PostgreSQL.
- **Auth today:** single JWT access token (60 min) in an httpOnly cookie.
  **Gap:** the product brief calls for revocable access/refresh-token
  pairs — not implemented yet. Treat as a near-term foundational item,
  not a nice-to-have (see §11).

## 4. Coding conventions

**Backend**
- Routes in `app/api/routes/`, one router per resource, included in
  `app/main.py`.
- Pydantic schemas (`app/schemas/`) are separate from SQLAlchemy models
  (`app/models/`) — never return a model instance directly from a route;
  always go through a `response_model`.
- Settings only via `app/core/config.py::get_settings()` (cached
  `pydantic-settings`), never `os.environ` directly in application code.
- New tables → new Alembic revision. **Watch the Postgres ENUM trap:**
  if a column uses a `postgresql.ENUM`, pass `create_type=False` on the
  column-level enum instance whenever the type is also created explicitly
  in the same migration — otherwise `create_table()` tries to create it
  a second time and fails on every fresh DB (this exact bug shipped in
  the first migration and was fixed in the second commit).
- Python `enum.Enum` columns: always set
  `values_callable=lambda x: [e.value for e in x]` on `sa.Enum(...)`.
  Without it, SQLAlchemy sends the member `.name` (`"STUDENT"`) instead
  of `.value` (`"student"`), which won't match a Postgres enum type
  created with lowercase values.

**Frontend**
- `frontend/lib/api.ts` is the *only* place that calls `fetch` against the
  backend. Route/page code calls `api.xxx()`, never raw `fetch`.
- Auth state lives in `frontend/lib/auth-context.tsx` (`useAuth()`), not
  per-page state.
- New UI primitives go in `components/ui/`, follow the existing
  `forwardRef` + `clsx` pattern.
- Tailwind tokens (`ink`, `muted`, `border`, `primary`, `accent`,
  `danger`) are defined in `tailwind.config.ts` — use them instead of
  raw hex/gray-scale classes so the palette stays centralized.

## 5. Security rules

- Passwords: never store plaintext. `passlib[bcrypt]` via
  `app/core/security.py`. **`bcrypt` must stay pinned to `4.0.1`** in
  `requirements.txt` — unpinned, pip resolves the latest bcrypt (5.x),
  which is incompatible with `passlib==1.7.4` and crashes every
  register/login call. Don't remove the pin without re-verifying.
- JWT secret, Grok key, DB URL: `.env` only, never in source, migrations,
  README, CLAUDE.md, logs, or committed anywhere. `.env` is gitignored in
  both `backend/` and root; only `*.env.example` files are tracked.
- Refresh tokens should be revocable (product requirement, not yet
  implemented — see §11).
- Minors: consent is modeled separately from authentication (not yet
  built — see §11). No unrestricted private messaging between students
  and mentors, ever — any mentorship messaging feature must be gated and
  scoped, not open DM.
- Career/assessment results are exploratory, never framed as a guaranteed
  outcome — applies to both backend response copy and frontend UI copy.
- AI Career Assistant: salary questions get ranges with the "varies by
  location/experience/company/role/education/skills" caveat, never a
  single confident number.

## 6. Database rules

- UUID primary keys (`uuid.uuid4`, Postgres `UUID` type).
- `created_at` / `updated_at` with `server_default=func.now()` (and
  `onupdate` for `updated_at`) on every table that represents a mutable
  entity.
- Proper foreign keys and indexes — no unnecessary denormalization.
- Alembic is the only way the schema changes. Never hand-edit the DB;
  if you did, write a migration that reflects it.
- Dashboard is config-driven, not hardcoded: `dashboard_sections` +
  `role_dashboard_sections` tables control visibility/ordering/enabled
  state per role. The frontend maps section keys to React components via
  a fixed registry — the DB can toggle/order/configure existing
  components, it can never cause arbitrary code execution. Not built yet
  (see §11).

## 7. Frontend/backend boundary

- `NEXT_PUBLIC_*` env vars are the **only** frontend env vars — anything
  without that prefix is invisible to the browser by design, so never
  expect it to be. Never put a secret behind `NEXT_PUBLIC_*`.
- `GROK_API_KEY`, `GROK_MODEL`, `AI_MAX_TOKENS`, `AI_TEMPERATURE`,
  `AI_REQUEST_TIMEOUT` are backend-only settings (already scaffolded in
  `app/core/config.py`, unused until the AI endpoint is built).

## 8. Internationalization

Target languages: English (fallback), Hindi, Bengali, Telugu, Punjabi.
User-selected, never inferred from state/location. Key-based translation
files for UI strings (no hardcoded strings in components); translation
tables for long-form DB content (careers, courses, announcements). Not
implemented yet — infra decision (e.g. `next-intl` vs custom) still open.

## 9. Testing

Backend:
```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pytest                      # fast, no DB needed — security + model metadata
```
These cover the hashing/JWT logic and the enum-column metadata directly
(the two DB-independent bug classes already hit once). They do **not**
exercise the API endpoints or run migrations — that needs a real Postgres:
```bash
# with DATABASE_URL pointed at a real/local Postgres in .env
alembic upgrade head
uvicorn app.main:app --reload
# then exercise /auth/register, /auth/login, /auth/me, /auth/logout
```
No endpoint-level integration test suite yet — worth adding
(`pytest` + a test-DB fixture, or `httpx.AsyncClient` against the app)
before Phase 3 (see §11).

Frontend:
```bash
cd frontend
npm install
npx tsc --noEmit   # type check
npm run lint       # next lint
npm run build      # production build
```
No component/e2e test framework configured yet (Vitest/Playwright etc.)
— open decision, not yet made.

## 10. Important product rules

- Don't build a giant hardcoded dashboard — always route through the
  section-registry + DB-config system (§6).
- Don't overbuild the AI assistant early: general Q&A first, RAG /
  profile-aware guidance / scholarship matching / navigation assistance
  are explicit future phases, not MVP.
- Don't implement expensive AI functionality, long conversation memory,
  or permanent storage of every AI conversation without a clear product
  need — MVP is short, stateless-ish conversations.
- Prefer simple → reliable → testable → extensible over impressive but
  fragile. Inspect existing code and reuse before rebuilding.

## 11. Current status & remaining phases

**Done (commits `f91c869`, `e54b693`):** JWT auth (register/login/
logout/me), 5-role user model, Alembic migration for `users`, Next.js
skeleton (landing/login/register/dashboard) wired to the API. Verified
end-to-end against a real Postgres instance. `bcrypt` pinned, Next.js
patched for CVE-2025-66478.

**Known gaps to close early (foundational, not feature work):**
- Refresh-token flow (revocable), not just a single access token.
- Guardian consent modeled separately from auth.
- Backend endpoint-level integration tests (need a test-DB story).
- Frontend test framework decision.

**Remaining feature phases (roughly in order):**
1. Dashboard shell + `dashboard_sections`/`role_dashboard_sections` +
   AI Career Assistant MVP (Grok, backend-only, safety/cost controls).
   This alone satisfies the product's first success criterion (register
   → login → dashboard → ask the assistant → get an answer).
2. Student discovery & assessment: onboarding, career library +
   translation tables, exploratory assessment, states/districts/schools
   reference data.
3. Learning: courses, modules, lessons, progress tracking.
4. Relationships & safety: parent/guardian linking, consent flow,
   mentorship with restricted (not open) messaging.
5. Admin & operations: admin panel, campaigns, registration/source
   tracking, announcements.
6. i18n rollout (Hindi/Bengali/Telugu/Punjabi) + later AI extensions
   (RAG, profile-aware guidance) — only once the above is stable.

## 12. Environment

`backend/.env` and `frontend/.env.local` are both gitignored and must be
created locally from their `.example` files. If `DATABASE_URL` is needed
and not already in `.env`, **ask the project owner for the real Neon
connection string — never invent one.**
