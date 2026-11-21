# PROGRESS — Alimzy International School Result Portal

> Read this file first when resuming. It records what is done, what is next, and key decisions.

## Current status

| Batch | Branch | Status |
|---|---|---|
| 0 — Setup & audit | `batch-0-audit` | ✅ Complete, awaiting review/merge |
| 1 — Repo hygiene & security | `batch-1-hygiene-security` | ⏸ Not started (waiting for "continue") |
| 2 — Backend domain & API | — | ⏸ Not started |
| 3 — Tests & CI | — | ⏸ Not started |
| 4 — Frontend foundation | — | ⏸ Not started |
| 5 — Frontend screens | — | ⏸ Not started |
| 6 — Deployment | — | ⏸ Not started |

## Batch 0 — done

- Verified repo, remote, branch, and commit (`fbd2de7` on `master`).
- Audited toolchain on Linux Mint (git, Python 3.12.3, uv 0.12.24, Node 24, npm 11, Docker 29 + Compose v5, gh authenticated, psql 16).
- Created `.venv` with `uv sync`; Django check passes; no migration drift.
- Applied all migrations on PostgreSQL 16 (disposable Docker container) and SQLite fallback.
- Ran the test suite: 0 tests (all four `tests.py` are placeholders).
- Ran `check --deploy`: 6 security warnings.
- Smoke-tested endpoints: login works (nested token shape), anonymous CRUD allowed, student enrollment returns 500.
- Read one screenshot and the logo image successfully; catalogued all design assets.
- Wrote `AUDIT.md` (full findings + proposed batch plan + decisions).
- Added `PROGRESS.md` (this file).

## Verification commands used

```bash
# venv + deps
uv sync

# static checks
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run

# Postgres (disposable)
docker run -d --name alimzy-audit-pg -e POSTGRES_DB=resultportal \
  -e POSTGRES_USER=resultportal -e POSTGRES_PASSWORD=audit_only_pw \
  -p 5433:5432 postgres:16-alpine
DB_NAME=resultportal DB_USER=resultportal DB_PASSWORD=audit_only_pw \
  DB_HOST=127.0.0.1 DB_PORT=5433 uv run python manage.py migrate --noinput
DB_NAME=resultportal DB_USER=resultportal DB_PASSWORD=audit_only_pw \
  DB_HOST=127.0.0.1 DB_PORT=5433 uv run python manage.py test -v 2
```

The disposable container and temporary SQLite file were removed afterwards.

## Key decisions / pending answers

1. Rotate the committed `SECRET_KEY` and Postgres password (compromised; still in git history).
2. Replace the legacy university domain (Department/Course/Level/Semester) with the school domain (Year/Term/Class/Arm/Subject/Enrollment)? Recommended: yes.
3. Grading scheme and CA/exam weights (WAEC A1–F9 vs A–F; e.g. CA 40 / Exam 60).
4. OpenAPI: drf-spectacular (recommended) vs drf-yasg.
5. PDF engine: WeasyPrint (recommended) vs ReportLab.
6. Parent role: include now or defer?
7. Logo font: Montserrat (OFL) acceptable?
8. Production email provider for password reset.
9. `seed_demo` passwords: env-provided (recommended) or random printed.
10. Commit `design/` assets (~3 MB) in Batch 1?

## Next batch (1) — planned work

- `git rm --cached` `.env`, `db.sqlite3`, `staticfiles/`, `.idea/`; fix `.gitignore`.
- Split settings into `base/dev/prod`, env-driven; `DEBUG=False` default.
- `DATABASE_URL`, CORS/CSRF, secure cookies/HSTS/SSL redirect/security headers.
- Complete `.env.example`.
- ruff + pre-commit; runtime/dev dependency groups.
- Multi-stage non-root Dockerfile with healthcheck; one-command compose.
- Full README.
- JWT: short access, rotation + blacklist, logout, throttled login, password validators.
- `/api/health/`.

## Notes for the next session

- Worktree: `/home/alimzy/projects/Alimzy International School`
- Default branch is `master` (not `main`); branch per batch from latest merged state.
- `design/` is untracked and untouched.
- `results` app is a placeholder; `drf-yasg` is installed but unused.
- Current login returns `{"user": {"access", "refresh", ...}}`; frontend will need the standard top-level token shape (change in Batch 2, documented).
- `.env` currently exists locally; do not print its values.
- gh CLI is authenticated and can open PRs.
- Missing system tooling for later batches: ImageMagick/librsvg/Inkscape, WeasyPrint libs, Montserrat/fonttools (install when needed).
