# Alimzy International School Result Portal

> **We don't give up here.** Established 2026.

Backend API for managing students, staff, academic sessions, results, report
cards and attendance at Alimzy International School.

> **Status:** Batch 0 (audit) and Batch 1 (hygiene/security) are complete. The
> current API is still the legacy university-shaped skeleton; the school domain
> (sessions, terms, classes, arms, subjects, results) lands in Batch 2. The
> React frontend lands in Batch 4–5. See [`AUDIT.md`](AUDIT.md) and
> [`PROGRESS.md`](PROGRESS.md).

## Stack

- Python 3.12 · Django 6 · Django REST Framework
- SimpleJWT (rotating refresh tokens + blacklist)
- PostgreSQL 16 (SQLite fallback for local development only)
- drf-spectacular (OpenAPI 3) · django-filter · django-cors-headers
- Gunicorn · WhiteNoise · Docker
- uv for dependency management · ruff + pre-commit

## Quick start (Docker, recommended)

```bash
cp .env.example .env
# Edit .env: set SECRET_KEY, POSTGRES_PASSWORD, and DATABASE_URL if needed.
# Generate a secret without printing it into your shell history:
python -c "import secrets; print(secrets.token_urlsafe(64))"

docker compose up --build
```

The API is then available at <http://localhost:8000>. The web container waits
for Postgres, applies migrations, and starts the development server.

- Health: <http://localhost:8000/api/health/>
- Swagger UI: <http://localhost:8000/api/docs/>
- ReDoc: <http://localhost:8000/api/redoc/>
- OpenAPI schema: <http://localhost:8000/api/schema/>
- Django admin: <http://localhost:8000/admin/>

Create the first superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

## Quick start (without Docker)

Requirements: Python 3.12+, [uv](https://docs.astral.sh/uv/), and either
PostgreSQL or SQLite for development.

```bash
uv sync
cp .env.example .env
# Set SECRET_KEY. For SQLite, set DATABASE_URL=sqlite:///db.sqlite3
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

`manage.py` defaults to `ResultPortal.settings.dev`, which loads `.env` and
falls back to SQLite when no database URL/legacy `DB_*` values are present.

## Environment variables

All values live in `.env` (never committed). See [`.env.example`](.env.example)
for the annotated list. The most important ones:

| Variable | Purpose | Default |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | Settings module | `ResultPortal.settings.dev` |
| `SECRET_KEY` | Django signing key | **required** |
| `DEBUG` | Debug mode | `False` (dev module defaults to `True`) |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | Database connection URL | SQLite in dev |
| `CORS_ALLOWED_ORIGINS` | Frontend origins | `http://localhost:5173` |
| `CSRF_TRUSTED_ORIGINS` | Trusted CSRF origins | empty |
| `JWT_ACCESS_MINUTES` | Access-token lifetime | `15` |
| `JWT_REFRESH_DAYS` | Refresh-token lifetime | `7` |
| `THROTTLE_LOGIN` | Login rate limit | `5/min` |
| `EMAIL_*` | SMTP configuration | console backend in dev |
| `SECURE_SSL_REDIRECT` | Force HTTPS in prod | `True` |

Production uses `ResultPortal.settings.prod`, which fails fast if
`SECRET_KEY`, `ALLOWED_HOSTS`, or the database configuration is missing.

## Commands

```bash
uv sync                              # install runtime + dev dependencies
uv run python manage.py check        # Django system checks
uv run python manage.py migrate      # apply migrations
uv run python manage.py test         # test suite (Batch 3 adds real tests)
uv run python manage.py createsuperuser
uv run python manage.py collectstatic --noinput
uv run ruff check .                  # lint
uv run ruff format --check .         # formatting check
uv run pre-commit run --all-files    # all hooks
```

Generate exported requirement files when a non-uv consumer needs them:

```bash
uv export --no-dev --format requirements-txt > requirements.txt
uv export --format requirements-txt > requirements-dev.txt
```

## Project structure

```
ResultPortal/
  settings/        base.py, dev.py, prod.py
  urls.py          API routes, docs, health
core/              custom User, Department, health endpoint
account/           Student, Staff, login/refresh/logout, enrollment
academics/         AcademicSession, Course, CourseRegistration (legacy)
results/           placeholder; replaced in Batch 2
design/            local reference assets (ignored) + generated brand outputs
AUDIT.md           Batch 0 findings and roadmap
PROGRESS.md        batch status and decisions
```

## Authentication

- `POST /api/auth/login/` — email + password → `{access, refresh, user}`
- `POST /api/auth/refresh/` — rotate refresh token (old token is blacklisted)
- `POST /api/auth/logout/` — blacklist a refresh token (requires access token)
- Access tokens last 15 minutes; refresh tokens last 7 days by default.
- Login is throttled (`THROTTLE_LOGIN`, default `5/min`).
- The DRF default permission is `IsAuthenticated`. Public endpoints are limited
  to health, login, refresh, and the API documentation.

## Security notes

- Never commit `.env`. It is ignored and untracked as of Batch 1.
- Rotate any secret that was ever committed. The historical `.env` and
  `docker-compose.prod.yml` contained credentials; treat them as compromised.
- Production settings enable HTTPS redirect, HSTS, secure cookies, nosniff,
  referrer policy and frame denial.
- Do not run `collectstatic` or the app with `DEBUG=True` in production.

## Tests

The current four `tests.py` files are placeholders, so `manage.py test` runs
0 tests. Batch 3 introduces pytest/pytest-django/factory_boy with coverage
targets and CI.

## License

Proprietary — Alimzy International School.
