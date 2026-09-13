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

- **Login identifier:** `users.email` is now nullable — a student who
  is a minor without an email can register with just `mobile_number`
  instead. At least one of the two is enforced by a DB CHECK constraint
  (`ck_users_email_or_mobile`), not just application code. `/auth/
  login` takes `identifier` (matched against either column), not
  `email`. Every other role still requires email (enforced in
  `UserCreate`'s role-conditional validator, not the DB — the DB only
  enforces the universal "at least one" rule).

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
pytest                      # fast unit tests + live-DB integration tests
```
Two kinds of tests now run together:
- **Unit tests** (no DB): security/JWT/OTP helpers, role-dependency
  logic, schema validation (incl. the role-conditional registration
  requirements), model metadata.
- **Integration tests** (`tests/test_integration_*.py`, using the
  `client`/`db_session`/`*_client` fixtures in `conftest.py`): run
  against a **real local Postgres** (needs a `postgres` OS user
  reachable via `su postgres` peer auth, matching how this repo's dev
  DB was set up) — resets the `unity_test` database and runs the real
  Alembic migrations (not `create_all`, since several migrations seed
  rows routes depend on) once per test run, then isolates every
  individual test in a rolled-back transaction. **This wipes whatever
  was in your local `unity_test` database** — don't point
  `DATABASE_URL` at anything you care about when running `pytest`.
  Covers the full auth lifecycle (register -> login -> refresh ->
  logout -> refresh-after-logout rejected), the role-security matrix
  (every role's protected endpoints reject every other role, and
  reject no auth at all), course enrollment/progress/continue-learning,
  assessment submission/scoring/weight-hiding, and the full guardian-
  relationship-to-OTP-consent-to-mentorship-request-to-session-to-
  feedback chain (the most business-logic-heavy flow in the app).

Endpoint coverage beyond the above (careers, campaigns, announcements,
school admin, dashboard config) is still verified manually per-feature
during development, not by this suite yet -- extending it is real
remaining work, not done.

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

**Backend (11 migrations, ~79 routes):** auth (revocable rotating
refresh tokens, login by email OR mobile number), 5 roles with
role-specific registration requirements enforced in `UserCreate`
(student: DOB/school/parent-info/address/district/state, email
optional; parent: email+mobile+student-info; mentor/school_admin:
email+mobile+DOB, school_admin also school name/location), identity/
role-profile split, languages (seeded) + a public GET /languages,
locations (schema only, no data), student onboarding, guardian
relationships, per-feature consent (dev-mode OTP), dashboard config
backend + frontend section registry, AI Career Assistant (Groq-
configured, still unverified live from this sandbox — network egress
blocks both api.groq.com and api.x.ai), career library (12 categories
seeded), courses/modules/lessons/enrollment/progress, campaigns +
best-effort attribution, `scripts/create_admin.py` bootstrap +
GET/PATCH /admin/users, career assessment (rule-based, 10 seeded
questions), mentorship foundation (gated on `has_active_consent`, no
chat), announcements (role + language filtered).

**Frontend:** login/register (role-specific dynamic form), dashboard,
career browsing, courses, assessment flow, mentorship (student +
mentor), parent (linked students + consent), full admin section (users,
careers, courses, campaigns, announcements, dashboard-sections). Dark/
light mode (CSS-variable-based, zero per-component changes needed) and
a language switcher live in the nav on every page including login/
register. Fraunces (display) + Manrope (body) typography.

Every feature was verified end-to-end as it was built: migration
upgrade/downgrade/upgrade, then a live curl (or, for anything
client-side-logic-heavy like the refresh-retry flow and the
registration payload shapes, a Node script replicating the frontend's
actual code) run of the happy path plus key negative cases. 53/53
backend pytest, frontend `tsc`/lint clean (0 errors, 0 warnings)
throughout.

**Known gaps:**
- AI provider (Groq) still unverified with a real live call — try from
  an environment with actual network access.
- A live-DB integration test suite exists (`tests/test_integration_*.py`,
  §9) covering auth lifecycle, the role-security matrix, course
  enrollment/progress/continue-learning, assessment submission/scoring/
  weight-hiding, and the full guardian-consent-to-mentorship-to-session-
  to-feedback chain. Careers/campaigns/announcements/school-admin/
  dashboard-config endpoints are still verified manually only —
  extending coverage to those is real remaining work, not done.
- Frontend test framework not chosen.
- `states`/`districts`/`schools` structured tables still have no data;
  registration now collects school/district/state as free text instead
  (see profiles.py docstrings) — the FK columns are reserved for a
  future structured-search feature, not currently read by anything.
- OTP delivery is dev-mode only; no real SMS provider.
- In-memory AI rate limiter is single-process only.
- Assessment question authoring (weighted options) has no admin form
  yet — flagged in the admin page itself, not faked.
- School-student matching (`GET /schools/me/students`) is by exact
  (case-insensitive) `school_name` text match — no verified link, so a
  spelling difference between a student's and a school admin's typed
  school name means that student silently doesn't show up.
- Real i18n now exists (`frontend/lib/i18n/{en,hi,bn,te,pa}.json` +
  `lib/language-context.tsx`'s `t()` hook, all 5 files key-parity
  checked) but is only wired into SiteNav, the homepage, and login/
  register so far -- every other page (careers, courses, assessment,
  mentorship, parent, admin, dashboard sections) still has hardcoded
  English strings. Extending `t()` to the rest of the app is real,
  substantial remaining work, not a small follow-up. Career/course
  *content* translation tables are a separate thing from this UI-string
  system and still aren't rendered through in the frontend either.
- Parent registration's `student_name` and student registration's
  `parent_name`/`parent_relation` are informational text only, not a
  verified link — the real link is still the separate guardian_
  relationship + consent flow (invite by email, verify, grant consent).
  Worth eventually reconciling (e.g., suggest a guardian invite
  pre-filled from what the student typed) but not done yet.

**Remaining work, roughly in order:**
1. Location seed data (a real states/districts/schools import) and,
   once that exists, deciding whether to switch student/school-admin
   registration from free text to structured FK pickers.
2. A live-DB integration test suite (currently all verification is
   manual/curl/Node-script-based, which doesn't run in CI).
3. Verify the AI provider actually answers, from a networked
   environment.
4. Real i18n: translated UI strings for all 5 languages, and wiring
   the existing career/course translation tables into the frontend.
5. A full end-to-end audit pass: role-security matrix, all 5 languages
   checked in the UI, performance/N+1 pass, error-handling pass.

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
