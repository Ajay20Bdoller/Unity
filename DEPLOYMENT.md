# Deploying Unity for a pilot launch

This is written for a small, controlled pilot (Option B: people you
personally know or vet, not open public signup). It assumes:
- A Neon Postgres database (or any Postgres) already exists.
- No real SMS provider yet (per CLAUDE.md — OTP stays dev-mode; you
  said you'll add this once there's budget for it).

## Nothing here is locked to Vercel/Railway specifically

The backend is plain FastAPI/Python, the frontend is plain Next.js —
neither depends on a specific host's proprietary APIs. Concretely:
- **Backend**: works on Render, Railway, Fly.io, Google Cloud Run,
  AWS (ECS/Fargate, Elastic Beanstalk, EC2), DigitalOcean App
  Platform, or a plain VPS running Docker — the `Dockerfile` in
  `backend/` builds a portable container image that runs anywhere;
  the `Procfile` is an alternative for hosts (Railway, Render, Heroku-
  style) that support that convention directly without needing a
  Dockerfile at all. Pick whichever your host prefers, not both.
- **Frontend**: Vercel is the path of least resistance for Next.js
  (built by the same company, zero-config), but Netlify, AWS Amplify,
  or a Docker container anywhere all work too.
- **Render specifically**: no code changes needed. Render supports
  both a `Procfile` and (more commonly) just setting a Build Command
  (`pip install -r requirements.txt`) and Start Command
  (`alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
  directly in its dashboard if it doesn't pick up the Procfile
  automatically — check whichever Render's UI shows you.
- **AWS later**: no code changes needed there either. The `Dockerfile`
  is what you'd point ECS/Fargate or App Runner at directly; the
  frontend could go on Amplify (which supports Next.js natively) or
  as its own container. Only the environment-variable-setting
  mechanism changes per host, not the app.

## Does CORS accept requests from any origin?

No — `CORS_ORIGINS` is a specific allowlist you configure (see step
3), not a wildcard. This is required, not just a choice: browsers
don't allow a wildcard `*` origin together with credentialed requests
(cookies), which this app depends on — so it has to be an exact list
of real origins regardless. Whatever frontend URL you deploy to must
be in this list or every API call will be silently blocked by the
browser.

## 1. Generate a real secret

Never deploy with the placeholder JWT_SECRET_KEY from `.env.example`.
Generate one and save it somewhere safe (a password manager) — you'll
paste it into the backend host's environment variables in step 3.

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

## 2. Point DATABASE_URL at the real database

Use Neon's **direct** (non-pooler) connection string for running
migrations, and the pooler connection string for the running app if
Neon gives you both — check whichever your Neon dashboard shows you.
If you're unsure, the direct one works for both and is the safer
default for a small pilot's traffic.

## 3. Deploy the backend (Railway recommended)

Railway is the simplest option here since it can build straight from
the `backend/` folder without a Dockerfile, and the `Procfile` in that
folder already tells it what to run.

1. New Railway project -> Deploy from GitHub repo -> select this repo,
   set the **root directory to `backend`**.
2. Set these environment variables in Railway's dashboard:

   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | your Neon connection string |
   | `JWT_SECRET_KEY` | the value from step 1 |
   | `ENVIRONMENT` | `production` |
   | `EXPOSE_DEV_OTP` | `true` — you're skipping real SMS for now (per your own call), so this is what lets you actually see OTPs to relay them yourself during the pilot. Set this back to unset/`false` the moment a real SMS provider exists — see `.env.example`'s comment on this for why. |
   | `CORS_ORIGINS` | your frontend's URL once you have it (step 4) — comma-separate if more than one, e.g. `https://yourapp.vercel.app,https://yourdomain.com`. Must be the exact origin the browser sends: no trailing slash. |
   | `GROK_API_KEY` | your Groq key, if you want the AI assistant live |
   | `GROK_MODEL` | `llama-3.3-70b-versatile` |
   | `GROK_BASE_URL` | `https://api.groq.com/openai/v1` |

3. Deploy. The `Procfile` runs `alembic upgrade head` automatically
   before starting the server, so migrations (including all seed data
   — languages, career categories, the sample course/assessment,
   Indian states) apply on first deploy with no extra step.
4. Railway gives you a URL like `https://something.up.railway.app` —
   that's your `NEXT_PUBLIC_API_URL` for the frontend in step 4.

> **Why `ENVIRONMENT=production` matters beyond just secure cookies:**
> your frontend (Vercel) and backend (Railway) will be on two
> completely different domains. Browsers treat that as "cross-site,"
> and a cookie's `SameSite=Lax` setting (the default for local dev)
> is **not sent on cross-site API calls at all** — only on top-level
> page navigations. Without `ENVIRONMENT=production` here, login would
> appear to work (the cookie gets set) but every subsequent request
> would look logged-out, because the browser silently withholds the
> cookie. `ENVIRONMENT=production` switches to `SameSite=None` +
> `Secure`, which is what actually works cross-domain. (This is also
> why curl-based testing during development never caught it — curl
> doesn't enforce SameSite policy the way real browsers do.)

## 4. Deploy the frontend (Vercel)

1. New Vercel project -> import this repo -> set the **root directory
   to `frontend`**.
2. Environment variable:

   | Variable | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | the Railway URL from step 3 |

3. Deploy. Vercel gives you a URL like `https://something.vercel.app`.
4. **Go back to Railway and update `CORS_ORIGINS`** to this real
   Vercel URL (you likely set a placeholder in step 3) — cookies and
   API calls from the frontend will otherwise be silently blocked by
   CORS. Redeploy the backend after changing it.

## 5. Create the first admin account

`POST /auth/register` refuses the `admin` role on purpose (see
CLAUDE.md) — the only way to create one is the CLI script, run once
against production:

```bash
# from the backend/ folder, with DATABASE_URL pointed at production
python -m scripts.create_admin --email you@example.com --name "Your Name" --mobile 9876543210
```

`--mobile` is optional but strongly recommended — it's what lets you
use `/forgot-password` to recover this account if you lose the
password, since that flow is mobile-only by design. Without it, there
is no self-service way to reset an admin's password.

## 6. Smoke-test checklist before inviting anyone

- [ ] Register a real test account for each role (student, parent,
      mentor, school_admin) and confirm registration + login works
- [ ] Log in as the admin, approve a test mentor from `/admin/mentors`
- [ ] Run through the full guardian-consent chain once, end to end —
      the OTP will show up as `dev_otp` in the network response (no
      SMS yet), which is fine for a pilot where you're walking people
      through it, but **make sure whoever's piloting this understands
      that step is you manually relaying it**, not something that
      arrives by text. Alternatively: `/admin/consent` lets you grant
      a consent directly (no OTP at all) once you've personally
      confirmed the parent's agreement some other way — the guardian
      link itself still needs the parent to verify it from their own
      account first, only the OTP step is skippable this way.
- [ ] Confirm the AI assistant answers (if you set the Groq key)
- [ ] Check the site loads correctly in both light and dark mode
- [ ] Try switching languages on the login/register page

## What's still true regardless of deployment

Everything in CLAUDE.md's "Known gaps" section still applies after
deployment — this guide gets the app *running* in production, it
doesn't change what's built. In particular: OTP-based consent isn't a
real identity check without real SMS. For Option B (a controlled pilot
where you personally know or can vet participants) that's a reasonable
trade-off; it would not be for open public signup.
