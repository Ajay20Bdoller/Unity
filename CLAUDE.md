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
- The frontend API client calls `/auth/refresh` automatically on a 401
  and retries once (`frontend/lib/api.ts` — verified against the real
  backend, including the exact retry control flow, not just unit-level).

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
- Minors: consent is modeled separately from authentication —
  `guardian_relationships` (student-initiated, parent-verified identity
  link) and `consent_records` (per-feature: MENTORSHIP, DATA_SHARING;
  dev-mode OTP only, no SMS provider wired up) are two distinct axes.
  Any sensitive feature must call `app.core.consent.has_active_consent`
  before proceeding — a verified relationship alone is **not** enough.
  No unrestricted private messaging between students and mentors, ever —
  any mentorship messaging feature must be gated by this and scoped, not
  open DM.
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

**Backend done (10 migrations, ~74 routes):** auth (revocable rotating
refresh tokens), 5 roles, identity/role-profile split, languages
(seeded), locations (schema only, no data), student onboarding,
guardian relationships, per-feature consent (dev-mode OTP), dashboard
config backend, AI Career Assistant (Groq-configured, unverified live —
see gaps), career library (12 categories seeded), courses/modules/
lessons/enrollment/progress, campaigns + best-effort attribution,
`scripts/create_admin.py` bootstrap, career assessment (rule-based,
10 seeded questions, exploratory results only), mentorship foundation
(expertise/languages/requests/accept-decline/sessions/feedback, gated
on `has_active_consent`, no chat), announcements (role + language
filtered, draft/publish, English fallback).

**Frontend:** still only login/register/dashboard (2 sections: welcome,
AI assistant card). None of career/course/assessment/mentorship/
campaign/announcement backend work has any UI yet.

Every feature above was verified end-to-end against a real Postgres
instance as it was built (migration upgrade/downgrade/upgrade, then a
live curl run of the happy path plus its key negative cases — e.g.
consent-gate blocking mentorship until granted, double-accept on a
mentorship request, duplicate feedback, audience-filtered announcements
showing the right set to each role, assessment weights never leaking
to students). 47/47 backend pytest (unit-level only — no live-DB
automated integration suite yet, see gaps). Frontend `tsc`/lint clean
throughout (unaffected by this round, which was backend-only).

**Known gaps:**
- **AI provider unverified live.** Confirmed Groq (`gsk_`-prefixed key,
  not xAI's Grok), `GROK_BASE_URL`/`GROK_MODEL` set accordingly — but
  this sandbox's network egress blocks both `api.groq.com` and
  `api.x.ai` outright (HTTP 403, `x-deny-reason: host_not_allowed`).
  Try the real call from an environment with actual network access.
- No frontend UI at all for: career browsing, courses, assessment,
  mentorship, campaigns, announcements. This is the single biggest
  remaining chunk of work — arguably bigger than everything backend
  above combined.
- No in-app "admin creates another admin" API — only the CLI script.
- No live-DB automated integration test suite (endpoint tests exist
  only for `/ai/chat`, which has no DB dependency). Everything else was
  verified manually via curl during development, not via CI-runnable
  tests.
- `states`/`districts`/`schools` have no data (seed/import mechanism
  not built).
- OTP delivery is dev-mode only; no real SMS provider.
- In-memory AI rate limiter is single-process only.
- Frontend test framework not chosen.
- i18n frontend infra (key-based translation files) not started —
  backend translation tables (careers) and language-scoped rows
  (announcements) exist, but nothing renders them in a UI yet.

**Remaining work, roughly in order of what unblocks the most:**
1. **Frontend build-out** — this is the real remaining project size.
   Needs, at minimum: career browsing + detail pages, course/lesson
   pages with progress UI, assessment flow (intro → questions →
   result), mentorship (browse mentors, request, view status), parent
   UI (linked students, consent status/actions), admin UI (all the
   admin endpoints above currently have zero UI), announcements feed,
   and i18n plumbing for all 5 languages.
2. Location seed data (a real states/districts/schools import).
3. A live-DB integration test suite (currently all verification is
   manual/curl-based, which doesn't run in CI).
4. Verify the AI provider actually answers, from a networked
   environment.
5. A full end-to-end audit pass once the above exists: role-security
   matrix (every role against every other role's endpoints), all 5
   languages checked in the UI, performance/N+1 pass, error-handling
   pass (400/401/403/404/409/422/500 all return clean messages, no
   stack traces) — this is what doc-21 actually asks for, and it can't
   be done honestly until there's a frontend to run it against.

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
