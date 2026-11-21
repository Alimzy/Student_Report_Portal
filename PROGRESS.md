# PROGRESS — Alimzy International School Result Portal

> Read this file first when resuming. It records what is done, what is next, and key decisions.

## Current status

| Batch | Branch | Status |
|---|---|---|
| 0 — Setup & audit | `batch-0-audit` | ✅ Complete, PR #1 open (not merged) |
| 1 — Repo hygiene & security | `batch-1-hygiene-security` | ✅ Complete, ready for review |
| 2 — Backend domain & API | `batch-2-backend-api` | ⏸ Not started (waiting for "continue") |
| 3 — Tests & CI | — | ⏸ Not started |
| 4 — Frontend foundation | — | ⏸ Not started |
| 5 — Frontend screens | — | ⏸ Not started |
| 6 — Deployment | — | ⏸ Not started |

Batch 1 was cut from `batch-0-audit` because the Batch 0 PR had not been merged yet. Merge Batch 0 first, then Batch 1.

---

## Batch 0 — done (summary)

- Repo/toolchain verified; `.venv` created with uv.
- Migrations applied on Postgres 16 and SQLite; 0 tests existed.
- `AUDIT.md` written with full findings, target gaps, and the batch plan.
- Design assets catalogued; image reading verified.
- Critical finding: tracked `.env` and hardcoded DB password (rotate).

---

## Batch 1 — done

### Repository hygiene
- Untracked (kept on disk): `.env`, `db.sqlite3`, `staticfiles/`, `.idea/`.
- Expanded `.gitignore` for secrets, SQLite, static/media, caches, IDE files, frontend artifacts, and design reference images.
- Added `.dockerignore` to keep secrets/local state out of images.
- Design reference screenshots/logo are now ignored (local only). Generated assets under `design/brand/` remain trackable.
- `.env.example` rewritten with comments and all supported variables.
- `docker-compose.prod.yml` no longer contains a hardcoded DB password.

### Settings
- Replaced `ResultPortal/settings.py` with a package:
  - `base.py` — shared, environment-driven.
  - `dev.py` — loads `.env`, DEBUG defaults on, SQLite fallback, console email.
  - `prod.py` — fails fast on missing secrets, enforces HTTPS/HSTS/secure cookies.
- `manage.py` defaults to `ResultPortal.settings.dev`; `wsgi.py`/`asgi.py` default to `prod`.
- `DEBUG` is off by default; production forces it off.
- `DATABASE_URL` via `dj-database-url`; legacy `DB_*` still supported; SQLite fallback only in dev.
- CORS and CSRF trusted origins come from env.
- Production: SSL redirect, proxy SSL header, HSTS (1 year, subdomains, preload), secure session/CSRF cookies, nosniff, referrer policy, frame denial.
- `/api/health/` is exempt from SSL redirect so container/platform probes work internally.

### Auth and API security
- DRF default permission is now `IsAuthenticated` (was effectively `AllowAny`).
- SimpleJWT: 15-minute access tokens, 7-day refresh tokens, rotation + blacklist after rotation, `UPDATE_LAST_LOGIN`.
- Added `/api/auth/refresh/` (rotation) and `/api/auth/logout/` (blacklist).
- Login is throttled at `5/min`; refresh at `30/min`; general anon/user throttles configured.
- Login response is now standard: `{access, refresh, user}` (tokens no longer nested under `user`).
- Login errors return proper 401s; logging no longer records submitted email addresses.
- Enrollment serializers now validate passwords with Django validators and check duplicate email/username.
- Fixed `KeyError: 'department'` in student/staff enrollment (now `department_code`).
- Fixed nested course viewset kwargs (`nested_1_pk`) so filtering/creation uses the department.
- Added drf-spectacular OpenAPI 3 docs at `/api/schema/`, `/api/docs/`, `/api/redoc/`.
- Removed unused `drf-yasg` and `loguru` dependencies.

### Tooling and Docker
- Added ruff (lint + format) config and `pre-commit` hooks; all hooks pass.
- Split dependencies into runtime and `dev` groups; exported pinned `requirements.txt` and `requirements-dev.txt`.
- Multi-stage Dockerfile: builder + slim runtime, non-root `app` user, collectstatic, Gunicorn, healthcheck.
- `docker-compose.yml` runs Postgres + Django with migrations in one command.
- Verified: image builds; compose stack reaches healthy; Gunicorn + prod settings serves health/docs; anonymous API returns 401.

### Verification results
- `manage.py check` — clean.
- `makemigrations --check --dry-run` — no drift.
- `manage.py migrate` — applies on a clean SQLite DB (and Postgres via compose).
- `manage.py test` — 0 tests (Batch 3 adds real tests).
- `ruff check` / `ruff format --check` / `pre-commit` — all pass.
- `check --deploy` (prod settings) — **0 warnings**. All six original warnings resolved:
  - W004 HSTS → `SECURE_HSTS_SECONDS`
  - W008 SSL redirect → `SECURE_SSL_REDIRECT`
  - W009 weak/insecure `SECRET_KEY` → strong env value required
  - W012 session cookie → `SESSION_COOKIE_SECURE`
  - W016 CSRF cookie → `CSRF_COOKIE_SECURE`
  - W018 `DEBUG` → forced `False` in prod
- Login throttle confirmed: five failures then HTTP 429.
- JWT rotation/logout confirmed: rotated refresh works; blacklisted refresh returns 401.

---

## Endpoints after Batch 1

### Public (no authentication)
| Method | URL | Why |
|---|---|---|
| GET | `/api/health/` | Docker/host health probe |
| POST | `/api/auth/login/` | Login |
| POST | `/api/auth/refresh/` | Token rotation |
| GET | `/api/schema/` | OpenAPI schema |
| GET | `/api/docs/` | Swagger UI |
| GET | `/api/redoc/` | ReDoc |
| — | `/admin/` | Django admin login page (admin content still protected) |

### Authenticated (previously public)
| Method | URL | Notes |
|---|---|---|
| CRUD | `/api/departments/` | Legacy; role rules in Batch 2 |
| CRUD | `/api/departments/{code}/course/` | Legacy nested route |
| CRUD | `/api/academics/` | Legacy academic sessions |
| POST | `/api/student-enroll/` | Legacy; should become admin-only in Batch 2 |
| POST | `/api/staff-enroll/` | Legacy; should become admin-only in Batch 2 |
| POST | `/api/auth/logout/` | Requires access token |

**Please confirm which of these should stay public.** Recommended: only health, login, refresh, and docs stay public; enrollment and all CRUD should be admin/teacher-scoped in Batch 2.

---

## Secrets to rotate (user action)

1. Django `SECRET_KEY` — previously committed in `.env`.
2. PostgreSQL password — previously committed in `.env`, `docker-compose.prod.yml`, and a code comment.
3. Any other system that reused that DB password.

The values remain in git history (commit `7933f45`). History was **not** rewritten and nothing was force-pushed. Treat both as compromised.

---

## Decisions confirmed by the user

1. Rotate secrets manually; no history rewrite.
2. Replace the legacy university domain with the school domain in Batch 2 (new migrations only).
3. Grading: A–F with configurable CA/exam weights and CA components.
4. OpenAPI: drf-spectacular.
5. PDF: WeasyPrint (ask before installing system packages).
6. Parent role: deferred until after Batch 5.
7. Logo font: Montserrat (OFL).
8. Email: env-driven SMTP; console backend in dev; provider chosen in Batch 6.
9. `seed_demo` passwords: env-provided, fail clearly if missing, never print them.
10. Commit only generated `design/brand/` assets and `DESIGN_NOTES.md`; keep reference images local/ignored.

---

## Next batch (2) — planned work

- New school domain: `SchoolProfile`, `AcademicYear`/`Session`, `Term`, `SchoolClass`, `ClassArm`, `Subject`, `TeacherAssignment`, `StudentEnrollment`, `AssessmentComponent`, `GradeScale`/`GradeBand`, `Result`, `ClassResult` (publish/lock), `Attendance`, score audit, verification tokens.
- Role permissions: Admin / Teacher / Student; students see own published results; teachers see assigned classes/subjects.
- Score entry, totals, grades, remarks, positions with ties, averages, publish/lock, audit trail.
- Attendance records and summary totals.
- CRUD endpoints with pagination/filter/search/ordering; consistent errors; `select_related`/`prefetch_related`; indexes; bulk CSV/Excel import.
- Report-card PDF (WeasyPrint), public verification endpoint, dashboard stats, recent activity.
- `seed_demo` command with env-provided demo passwords.
- Keep legacy endpoints working or document exact removals.

---

## Notes for the next session

- Worktree: `/home/alimzy/projects/Alimzy International School`
- Branches: `batch-0-audit` (PR #1), `batch-1-hygiene-security` (this batch).
- Default branch is `master`.
- Local `.env` still exists (ignored) and contains the old values; rotate them and set `DATABASE_URL` for non-Docker development.
- `db.sqlite3` is a 0-byte leftover and is ignored.
- Tests are still placeholders; Batch 3 adds pytest/factory_boy/coverage.
- `results` app is still a placeholder; Batch 2 replaces it.
- `design/` reference files are on disk but ignored; `design/brand/` is reserved for generated logo exports.
- Missing system tooling for later batches: ImageMagick/librsvg/Inkscape, WeasyPrint libs, Montserrat/fonttools. Ask before running `sudo`.
- Do not print real secrets; do not force-push or rewrite history.
