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

Five roles, all first-class: **STUDENT, PARENT, MENTOR, SCHOOL_ADMIN,
ADMIN**. The AI Career Assistant is available to every authenticated
role, not just students. Only STUDENT/PARENT/MENTOR/SCHOOL_ADMIN can
self-register — ADMIN accounts are provisioned separately, never via
open registration (see §5).

## 2. Architecture

```
Next.js (frontend)
   │  REST/JSON, JWT access token + refresh token in httpOnly cookies
   ▼
FastAPI (backend)
   │  SQLAlchemy
   ▼
Neon PostgreSQL

FastAPI ──▶ Grok API   (AI Career Assistant; backend-only, never from frontend)
```

Hard rule: the frontend **never** talks to Postgres or Grok directly.
Everything goes through the FastAPI REST API. Never trust a role/identity
claim from the frontend — every protected route re-resolves the user from
the access token server-side (see `require_*` deps in §4).

## 3. Tech stack

- **Frontend:** Next.js (App Router) 15.5.x, TypeScript (strict), Tailwind
  CSS, custom lightweight UI components (`frontend/components/ui/`) —
  shadcn/ui not yet pulled in, current components follow its conventions
  so migrating later is low-friction.
- **Backend:** FastAPI, Pydantic v2, SQLAlchemy 2.x (typed `Mapped[...]`
  style), Alembic, `python-jose` for JWT, `passlib[bcrypt]` for hashing.
- **DB:** Neon PostgreSQL.
- **Auth:** short-lived JWT access token (15 min) + revocable, rotating
  opaque refresh token (30 days), both httpOnly cookies (`refresh_token`
  cookie is scoped to `path=/auth`). Refresh tokens are stored as a
  SHA-256 hash only (`refresh_tokens` table, never plaintext). Every
  `/auth/refresh` call revokes the presented token and issues a new pair
  — a reused (already-rotated) token is refused, which catches replay of
  a stolen token.

## 4. Coding conventions

**Backend**
- Routes in `app/api/routes/`, one router per resource, included in
  `app/main.py`.
- Pydantic schemas (`app/schemas/`) are separate from SQLAlchemy models
  (`app/models/`) — never return a model instance directly from a route;
  always go through a `response_model`.
- Identity vs. role profile: `users` holds only identity/auth fields
  (email, password hash, role, is_active, preferred_language,
  timestamps). Role-specific fields live in their own 1:1 table —
  `students`, `parents`, `mentors`, `school_admin_profiles` — keyed by
  `user_id`. Never add a role-specific column to `users`. Registering a
  user always creates the matching profile row in the same transaction
  (see `_PROFILE_MODEL_BY_ROLE` in `app/api/routes/auth.py`).
- Authorization: use the `require_student` / `require_parent` /
  `require_mentor` / `require_school_admin` / `require_admin`
  dependencies from `app/api/deps.py` (built on a `require_role(*roles)`
  factory) to gate role-specific routes. These re-check the
  server-resolved user's role — they don't and shouldn't trust anything
  from the client.
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
- Renaming an existing Postgres enum value: `ALTER TYPE ... RENAME VALUE
  'old' TO 'new'` works fine inside Alembic's transactional DDL (unlike
  `ADD VALUE`, which historically couldn't run in the same transaction).

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
- The frontend API client does not yet call `/auth/refresh` on a 401 —
  that's still open (see §11).

## 5. Security rules

- Passwords: never store plaintext. `passlib[bcrypt]` via
  `app/core/security.py`, minimum 8 characters enforced server-side
  (`UserCreate` validator) — never rely on the frontend's `minLength`
  alone. **`bcrypt` must stay pinned to `4.0.1`** in `requirements.txt`
  — unpinned, pip resolves the latest bcrypt (5.x), which is
  incompatible with `passlib==1.7.4` and crashes every register/login
  call. Don't remove the pin without re-verifying.
- JWT secret, Grok key, DB URL: `.env` only, never in source, migrations,
  README, CLAUDE.md, logs, or committed anywhere. `.env` is gitignored in
  both `backend/` and root; only `*.env.example` files are tracked.
- Refresh tokens are revocable (implemented — §3). Logout revokes the
  presented refresh token; a rotated-away token is refused on reuse.
- Registration: only STUDENT/PARENT/MENTOR/SCHOOL_ADMIN can self-register
  (`SELF_REGISTERABLE_ROLES` in `app/models/user.py`). ADMIN is
  deliberately excluded — provision admin accounts via seed script or an
  existing admin's admin-API action once that exists, never open signup.
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

- UUID primary keys (`uuid.uuid4`, Postgres `UUID` type) — except 1:1
  profile tables (`students`, `parents`, `mentors`,
  `school_admin_profiles`), which use `user_id` itself as the primary
  key (no separate surrogate key for a 1:1 relationship).
- `created_at` / `updated_at` with `server_default=func.now()` (and
  `onupdate` for `updated_at`) on every table that represents a mutable
  entity.
- Proper foreign keys and indexes — no unnecessary denormalization.
- Alembic is the only way the schema changes. Never hand-edit the DB;
  if you did, write a migration that reflects it.
- Fixed platform reference data with a small, stable row count (e.g. the
  5 UI `languages`) can be seeded directly inside its creating migration
  via `op.bulk_insert`. Larger/variable "sample content" seed data
  (careers, courses, assessment questions, real school/location imports)
  belongs in the separate seed process (§11), not a migration.
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

Target languages: English (fallback), Hindi, Bengali, Telugu, Punjabi —
seeded in the `languages` table (`code`, `name`, `native_name`,
`is_active`). `users.preferred_language` is now a real FK to
`languages.code` (not a free string). `PATCH /users/me/language`
updates it, rejecting any code not in `languages`. User-selected, never
inferred from state/location. Key-based translation files for UI
strings (no hardcoded strings in components); translation tables for
long-form DB content (careers, courses, announcements) — frontend i18n
infra itself not implemented yet (e.g. `next-intl` vs custom still open).

## 9. Testing

Backend:
```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pytest                      # fast, no DB needed
```
Covers: password hashing (incl. the bcrypt-72-byte regression), JWT
access-token roundtrip, refresh-token generation/hashing/expiry, the
role-enum-column metadata, and every `require_*` role dependency
(allows its own role, 403s every other role). These do **not** exercise
the live API endpoints or run migrations — that needs a real Postgres:
```bash
# with DATABASE_URL pointed at a real/local Postgres in .env
alembic upgrade head
uvicorn app.main:app --reload
# then exercise /auth/register, /auth/login, /auth/refresh, /auth/logout,
# /auth/me, /users/me/language
```
No endpoint-level integration test suite yet (`httpx.AsyncClient` /
`TestClient` against a test DB) — worth adding before Phase 3 (§11).

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

**Done (commits `f91c869`, `e54b693`, `e77cc82`, and the auth-overhaul
commit on top):** JWT auth with short-lived access + revocable rotating
refresh tokens, role rename to STUDENT/PARENT/MENTOR/SCHOOL_ADMIN/ADMIN,
identity/role-profile split (`students`/`parents`/`mentors`/
`school_admin_profiles`), `languages` table (seeded) with a real FK from
`users.preferred_language`, `states`/`districts`/`schools` location
tables (schema only, no data yet), role-based `require_*` FastAPI
dependencies, admin-cannot-self-register restriction, server-side
password length validation. Verified end-to-end (register all 4 roles,
duplicate/invalid rejections, login, refresh rotation + reuse rejection,
logout, refresh-after-logout rejection, language update + invalid-code
rejection, all 5 role dependencies) against a real Postgres instance.
Next.js patched for CVE-2025-66478, `bcrypt` pinned.

**Known gaps to close early (foundational, not feature work):**
- Frontend doesn't yet call `/auth/refresh` on a 401 — access tokens
  are short (15 min), so this needs wiring before it's usable end to end.
- Guardian consent modeled separately from auth.
- Backend endpoint-level integration tests (need a test-DB story) —
  current coverage is unit-level only (no live DB in CI yet).
- Frontend test framework decision.
- `states`/`districts`/`schools` have no data yet — need the seed/import
  mechanism (explicitly: no giant hardcoded dataset in source).

**Remaining feature phases (roughly in order):**
1. Dashboard shell + `dashboard_sections`/`role_dashboard_sections` +
   AI Career Assistant MVP (Grok, backend-only, safety/cost controls).
   This alone satisfies the product's first success criterion (register
   → login → dashboard → ask the assistant → get an answer).
2. Student onboarding API (uses the `students` table fields already in
   the schema), guardian relationship + consent model, location seed data.
3. Career library (categories, careers, translations, related careers,
   student interests).
4. Courses + modules + lessons + enrollment + progress.
5. Career assessment (rule-based scoring, not AI, ~10-15 seed questions).
6. Campaigns + registration/source tracking.
7. Mentorship foundation (profile, languages, expertise, availability,
   manual/admin matching — no open chat).
8. Announcements, admin APIs for everything above, comprehensive backend
   test suite, then the full frontend (routes for all 5 roles + i18n),
   then a full end-to-end verification pass.

## 12. Environment

`backend/.env` and `frontend/.env.local` are both gitignored and must be
created locally from their `.example` files. If `DATABASE_URL` is needed
and not already in `.env`, **ask the project owner for the real Neon
connection string — never invent one.**

**Neon connection strings:** use the **direct** (no `-pooler` in the
hostname) connection string for Alembic migrations; use the **pooled**
(`-pooler`) string for the running app. Mixing these up doesn't always
fail loudly — pooled connections run PgBouncer in transaction mode,
which silently breaks session-level features some migration tooling
can depend on.

**Network note for whichever Claude session is running this:** a
plain chat sandbox (no MCP/agentic DB access) typically cannot open a
raw TCP connection to an arbitrary external Postgres host like Neon —
only a fixed allowlist of package-registry/GitHub domains. If that's
your situation: build and verify migrations against a local/throwaway
Postgres instead (same engine, same DDL — a valid stand-in), then hand
the project owner the exact `alembic upgrade head` (and later, seed)
command to run themselves against the real Neon URL. Don't assume this
limitation applies to every environment (Claude Code, a CI runner, or
the user's own machine may have full network access) — verify for the
current environment rather than assuming either way.
