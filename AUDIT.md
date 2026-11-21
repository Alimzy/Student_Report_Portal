# AUDIT — Alimzy International School Result Portal

- **Date:** 2026-11-21
- **Repo:** `github.com/Alimzy/Student_Report_Portal` (default branch `master`)
- **Local path:** `/home/alimzy/projects/Alimzy International School`
- **Audited commit:** `fbd2de7` ("Final setup")
- **Audit branch:** `batch-0-audit` (cut from `master`; only `AUDIT.md` and `PROGRESS.md` added)
- **Scope:** Batch 0 only. No feature code, no behaviour changes.

---

## 1. Repository verification

| Check | Result |
|---|---|
| Working directory is the repo | ✅ Yes (`.git` present, remote matches) |
| Remote | `https://github.com/Alimzy/Student_Report_Portal.git` |
| Current branch before audit | `master`, clean except untracked `design/` |
| Commit history | 6 commits; latest `fbd2de7` |
| Tracked files | 677 (≈600 are committed `staticfiles/`) |
| `design/` | **Untracked** (10 screenshots + 1 logo template + empty `brand/`) |
| `README.md` | 0 bytes |
| Existing tests | 4 placeholder `tests.py` files, **0 tests** |

The prompt's project summary is accurate: Django 6 + DRF, SimpleJWT, drf-yasg (installed but unused), PostgreSQL via psycopg2, Gunicorn, WhiteNoise, Docker; apps `account`, `academics`, `results`, `core`; project package `ResultPortal`; no frontend. The code is a **university-style skeleton** (Department/Course/Level/Semester/matric number), not a school portal. Most target features do not exist.

---

## 2. Toolchain (Linux Mint)

| Tool | Version found | Status |
|---|---|---|
| git | 2.43.0 | ✅ |
| Python | 3.12.3 | ✅ (Django 6 requires ≥ 3.12) |
| uv | 0.12.24 | ✅ used for venv + deps |
| pip | 24.0 (system) | ✅ |
| poetry | — | not installed (not needed; uv is used) |
| Node.js | v24.22.3 | ✅ |
| npm | 11.19.1 | ✅ |
| pnpm | — | not installed; optional (`corepack enable`) |
| Docker | 29.10.0 | ✅ daemon reachable |
| Docker Compose | v5.7.1 | ✅ |
| gh CLI | 2.45.0, authenticated as `Alimzy` (scopes: repo, workflow, gist, read:org) | ✅ PRs can be opened |
| psql | 16.15 | ✅ |
| PostgreSQL server | Local instance on `:5432` (auth failed for the committed credentials — expected) | ✅/⚠️ |
| ImageMagick (`convert`/`magick`) | missing | needed to export logo PNG/ICO in Batch 4 |
| `rsvg-convert` / Inkscape | missing | needed for SVG → PNG/ICO |
| WeasyPrint CLI + system libs | missing | needed for PDF report cards in Batch 2 |
| Montserrat font / fonttools | missing | needed to outline logo text |

Install suggestions (Batch 1/4, when needed):

```bash
sudo apt update
sudo apt install -y librsvg2-bin imagemagick fonts-montserrat
# WeasyPrint runtime libs (if the distro package is unavailable):
sudo apt install -y libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
  libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info
# Optional pnpm:
corepack enable && corepack prepare pnpm@latest --activate
```

If `fonts-montserrat` is not in the Mint repos, download Montserrat (SIL OFL 1.1) from Google Fonts and commit it under `design/fonts/`.

---

## 3. Environment verification

A project-local `.venv` was created with `uv sync` (23 packages, Python 3.12.3). No repo files were changed.

| Check | Command | Result |
|---|---|---|
| Django system check | `uv run python manage.py check` | ✅ 0 issues |
| Migration drift | `makemigrations --check --dry-run` | ✅ no changes detected |
| Migrate (Postgres 16) | disposable Docker container on `:5433` | ✅ all migrations applied |
| Migrate (SQLite fallback) | temporary `/tmp` settings module | ✅ all migrations applied |
| Test suite | `manage.py test` | ✅ exit 0 — **0 tests found** |
| Deployment check | `manage.py check --deploy` | ⚠️ 6 warnings (HSTS, SSL redirect, weak/insecure `SECRET_KEY`, secure session/CSRF cookies, `DEBUG=True`) |

**Smoke tests** (Django test client, temporary DB):

| Request | Result | Meaning |
|---|---|---|
| `POST /api/auth/login/` with email/password | `200`, body `{"user": {...}}` | Login works, but tokens are nested non-standardly |
| `GET /api/departments/` anonymous | `200` | Department CRUD is public |
| `GET /api/academics/` anonymous | `200` | Academic-session CRUD is public |
| `POST /api/student-enroll/` | `500` | `KeyError: 'department'` (serializer exposes `department_code`) |

The disposable Postgres container and temporary SQLite file were removed after verification.

---

## 4. Architecture

```
ResultPortal/          settings, root urls, wsgi/asgi
core/                  custom User (email login), Department, constants
account/               Student, Staff, enrollment + login views
academics/             AcademicSession, Course, CourseRegistration
results/               one orphan "Course" model; no API, no admin, no urls
design/                screenshots + logo template (untracked)
staticfiles/           committed collectstatic output (~600 files)
Dockerfile, docker-compose.yml, docker-compose.prod.yml
.github/workflows/ci-cd.yml
```

`results` is **not** included in `ResultPortal/urls.py`. `drf-yasg` is a dependency but is not installed as an app and has no routes. There is no `REST_FRAMEWORK`, `SIMPLE_JWT`, CORS, media, email, logging, or security configuration.

---

## 5. Data models and relationships

| Model | PK | Key fields | Relationships / notes |
|---|---|---|---|
| `core.User` | `id` | `email` (unique, `USERNAME_FIELD`), `username`, `role`, `is_active=False` by default | Custom user; `is_staff`; no `Role` enum |
| `core.Department` | `department_code` (char) | `name`, `is_active` | University-style; referenced by students/staff/courses |
| `account.Student` | **`matric_number`** (char) | `level`, `status`, `entry_year` | 1-1 `User` (`student_profile`), FK `Department`; table name contains a space (`"student account"`) |
| `account.Staff` | `id` | `designation` | 1-1 `User` (PROTECT), FK `Department`; no role limit |
| `academics.AcademicSession` | `id` | `name`, `year`, `semester`, `is_current` | Unique `(year, semester)`; no term model |
| `academics.Course` | **`course_code`** (char) | `title`, `credit_units`, `level`, `semester` | FK `Department`; `update_at` uses `auto_now_add` by mistake |
| `academics.CourseRegistration` | `id` | `register_at` | FKs Student/Course/Session; unique triple; **no viewset** |
| `results.Course` | `id` | `score`, `grade` (max 1 char), `grade_points`, `is_published` | FK `Staff` (`uploaded_by`); **orphan**: no student, subject, term, or class link. Unusable as-is. |

Target domain (SchoolProfile, AcademicYear, Term, Class/Arm, Subject, TeacherAssignment, Enrollment, Assessment weights, GradeScale, Result, Attendance, AuditLog, Verification) is absent.

---

## 6. Endpoints and permissions

DRF has no `DEFAULT_PERMISSION_CLASSES`, so the global default is **`AllowAny`**.

| Method | URL | Permission | Notes |
|---|---|---|---|
| — | `/admin/` | Django admin session | Admin UI |
| GET/POST | `/api/departments/` | **Anonymous** | Full CRUD |
| GET/PUT/PATCH/DELETE | `/api/departments/{code}/` | **Anonymous** | Full CRUD |
| GET/POST | `/api/departments/{code}/course/` | **Anonymous** | Nested course CRUD |
| GET/PUT/PATCH/DELETE | `/api/departments/{code}/course/{code}/` | **Anonymous** | Nested course CRUD |
| GET/POST | `/api/academics/` | **Anonymous** | Session CRUD |
| GET/PUT/PATCH/DELETE | `/api/academics/{id}/` | **Anonymous** | Session CRUD |
| POST | `/api/student-enroll/` | **Anonymous** | Broken (500) |
| POST | `/api/staff-enroll/` | **Anonymous** | Creates staff users; broken similarly |
| POST | `/api/auth/login/` | Anonymous | Email + password → nested JWT |
| — | `/api/refresh/`, `/api/logout/`, password reset/change | — | **Missing** |
| — | `/api/docs`, `/api/schema` | — | **Missing** (drf-yasg unused) |
| — | `/api/health/` | — | **Missing** |

No pagination, filtering, search, ordering, throttling, or consistent error envelope anywhere.

---

## 7. Auth flow (current)

1. `POST /api/auth/login/` with `email` + `password`.
2. `CustomTokenObtainSerializer` extends SimpleJWT's `TokenObtainSerializer`, calls `super().validate()`, then issues `RefreshToken.for_user()`.
3. Response is `{"user": {"id", "refresh", "access", "email", "username", "role"}}` — **tokens are nested under `user`**, unlike the standard `{access, refresh}` shape. No refresh endpoint is exposed.
4. `LoginView` catches every exception and returns a bare `400` or `404` with no error body; it logs the submitted email.
5. `User.is_active` defaults to **`False`**; enrollment creates inactive users, so they cannot log in until an admin activates them. There is no activation or password-reset flow.
6. `User.is_admin` calls `self.Role.ADMIN`, but the model has no `Role` enum → `AttributeError` if used.

SimpleJWT defaults apply: 5-minute access token, 1-day refresh, **no rotation, no blacklist** (the blacklist app is not installed).

---

## 8. Settings review (`ResultPortal/settings.py`)

- Lines 9–13 of the module docstring contain a corrupted paste (`the full list of set', } } tings...`). Harmless syntactically, but should be cleaned.
- `DEBUG = True` hardcoded.
- `SECRET_KEY` read from env with no fallback or startup validation; `ALLOWED_HOSTS` includes a raw public IP.
- Database is PostgreSQL-only via `DB_*` variables; no `DATABASE_URL`, no SQLite fallback, no connection reuse/SSL options.
- No `REST_FRAMEWORK`, `SIMPLE_JWT`, `CORS`, `CSRF_TRUSTED_ORIGINS`, `MEDIA_*`, `EMAIL_*`, `LOGGING`, or `SECURE_*` settings.
- `drf-yasg` installed but not registered.
- `TIME_ZONE = "UTC"`; a Nigerian school likely wants `Africa/Lagos`.
- `STATIC_ROOT` + WhiteNoise manifest storage configured; `STATIC_URL` is relative (`static/`) rather than `/static/`.
- Password validators exist, but enrollment serializers never call `validate_password()`.
- `is_active=False` default is a deliberate activation gate, but no activation workflow exists.

---

## 9. Findings

### 9.1 Security

| # | Severity | Finding |
|---|---|---|
| S1 | **Critical** | `.env` is tracked and contains a real `SECRET_KEY` and database password. `docker-compose.prod.yml` hardcodes the same DB password, and `account/serializer.py` contains it in a comment. **Rotate the Django `SECRET_KEY` and the Postgres password.** The values remain in git history (commit `7933f45`) even after `git rm --cached`; history rewrite or key rotation is required. |
| S2 | **Critical** | All API endpoints are effectively anonymous (`AllowAny` default), including Department/Course/Session CRUD and both enrollment endpoints. Anyone can create users or edit academic data. |
| S3 | **High** | `DEBUG=True` in every environment; detailed tracebacks and settings leak on errors. |
| S4 | **High** | No login throttling/rate limit or lockout → credential stuffing and brute force. |
| S5 | **High** | No JWT rotation, blacklist, logout, or refresh endpoint; refresh lifetime is the SimpleJWT default (1 day) and tokens are returned in a non-standard envelope. |
| S6 | **High** | Enrollment accepts any password without running Django's password validators; `set_password()` bypasses them. |
| S7 | **High** | No CORS/CSRF trusted-origin configuration, secure cookies, HSTS, SSL redirect, or security headers. `check --deploy` reports 6 warnings. |
| S8 | **Medium** | Integrity errors are returned to clients via `str(e)`, leaking table/constraint names. |
| S9 | **Medium** | Login logs user emails; no structured logging/redaction. |
| S10 | **Medium** | No object-level permissions or role checks; any authenticated user (once permissions are added) could read other students' data unless scoped. |
| S11 | **Medium** | CI uses long-lived AWS access keys stored as GitHub secrets and triggers on `main` while the default branch is `master`, so it never runs. |
| S12 | **Medium** | Docker image runs as root, has no healthcheck, and ships build tooling in the final layer. |
| S13 | **Low** | No audit trail for score changes; no verification tokens for report cards. |
| S14 | **Low** | `matric_number` uses a 4-digit random suffix and is the primary key → collision risk and 500s. |

### 9.2 Bugs

| # | Location | Bug |
|---|---|---|
| B1 | `account/views.py` | `serializer.validated_data['department']` — serializer field is `department_code`; both enrollment endpoints raise `KeyError` → **HTTP 500** (confirmed). |
| B2 | `core/models.py` | `User.is_admin` references `self.Role.ADMIN`; no `Role` enum exists → `AttributeError`. |
| B3 | `account/models.py` | `Student.is_active` returns the status string; `"suspended"` is truthy, so the property is misleading. |
| B4 | `results/models.py` | Duplicate `Course` model; `grade` max length 1 cannot store `A1`/`F9`; `grade_points` is an integer but defaults to `0.0`; no student/subject/term linkage. |
| B5 | `academics/models.py` | `Course.update_at` uses `auto_now_add` instead of `auto_now`. |
| B6 | `core/admin.py` | `UserAdmin` cannot edit `role` or `username` (not in `fieldsets`); `list_display` omits role/active state. |
| B7 | `account/views.py` | `LoginView` swallows all exceptions and returns empty 400/404 responses; 404 is used for invalid credentials (should be 401). |
| B8 | `academics/serializers.py` | `CourseSerializer.create` depends on `department_id` in context; no direct course endpoint exists, so the create path is only reachable via the nested router. |
| B9 | `core/views.py` / `academics/urls.py` | Large blocks of commented-out dead code. |
| B10 | `main.py` | Unused "Hello from resultportal" entry point. |
| B11 | `.env.example` | Typo `DDBUG`, missing most variables, no newline, no comments. |

### 9.3 Dead code / repo hygiene

- Tracked generated/local files: `.env`, `db.sqlite3` (0 bytes), `staticfiles/` (~600 files), `.idea/`.
- `.gitignore` only covers Python bytecode and `.venv`; it does not ignore `.env`, SQLite, static output, media, IDE files, or test artifacts.
- `README.md` is empty.
- `design/` is untracked and should be committed (≈3 MB) so future sessions/clones retain the reference assets.
- `results` app is a placeholder (no serializers, urls, admin, views, tests).
- `CourseRegistration` model/serializer exist but are unreachable.
- `uv.lock` is tracked (good); `pyproject.toml` has no dev-dependency group or lint/test tooling.
- `drf-nested-routers` is used only for the legacy nested course route.

### 9.4 Performance

- No pagination → every list endpoint returns the full table.
- No `select_related`/`prefetch_related`; currently masked because serializers expose few relations, but will cause N+1 once student/course/result nesting is added.
- No indexes beyond PK/unique/FK defaults; results and attendance will need composite indexes `(student, term)`, `(school_class, term)`, `(teacher, class, subject)`.
- No bulk-write transactions or `bulk_create`/`bulk_update` paths.
- `staticfiles/` in git bloats clones and CI checkouts.

### 9.5 Missing validation

- Score ranges, CA/exam weights, grade boundaries, and position ties (no models yet).
- Password strength on enrollment.
- `entry_year` range and consistency with `level`.
- Session date ordering; only one `is_current` session.
- Department/course code format; course credit bounds are present but not enforced at serializer level.
- File upload type/size limits (no uploads yet).
- Duplicate/unique error messages are raw database errors.

### 9.6 Missing pieces for a real result portal

SchoolProfile/branding; academic year + 3 terms; classes + arms; subjects; teacher–subject–class assignments; student enrollment per class/arm; configurable CA components and grading scale; score entry with audit trail; positions/averages; publish/lock; attendance; report-card PDF + print view; verification page/QR; dashboards and recent activity; CSV/Excel import; role-scoped APIs; auth refresh/logout/reset; pagination/filter/search/ordering; OpenAPI docs; health check; seed command; tests/CI; frontend; deployment.

---

## 10. Design assets

`design/` contains:

| File | Size | Notes |
|---|---|---|
| `01_Dashboard.png` | 1095×1404 | Full admin dashboard reference |
| `02_Student_Management.png` | 1110×953 | Student list/table reference |
| `03_Teacher_Management.png` | 1110×953 | Teacher list reference |
| `04_Academic_Management.png` | 1095×1045 | Sessions/terms reference |
| `05_Attendance_Monitor.png` | 1095×1380 | Attendance reference |
| `06_Examination_and_result.png` | 1095×1356 | Exams/results reference |
| `07_Classes_and_Subject.png` | 1095×984 | Classes/subjects reference |
| `08_Report_analytics.png` | 1095×1237 | Analytics reference |
| `09_users_and_roles.png` | 1095×991 | Users/roles reference |
| `10_System_setting.png` | 1095×984 | Settings reference |
| `Education logo and minimal school badge design template.jpeg` | 736×736 | Badge logo template |
| `brand/` | empty | Output folder for the rebuilt Alimzy brand |

**Image-reading proof (I can read images):**

- **`01_Dashboard.png`:** A light dashboard with a dark navy left sidebar (RUEMP logo, grouped navigation, active Dashboard item, status card at the bottom), a white top bar with page title/subtitle, global search, notification/help icons and a user avatar, then a pale-blue content area with a small uppercase eyebrow, a greeting headline, Export/Register actions, summary cards with tinted icon tiles and trend deltas, a large enrollment line chart, a donut chart, a province bar list, a performance bar chart and an attendance donut.
- **`Education logo and minimal school badge design template.jpeg`:** A circular school badge with a navy outer ring of curved white placeholder text, an orange inner ring, a navy open book with a blue spine, an orange flame with radiating light rays above it, blue laurel branches on both sides, two orange stars, and a navy ribbon banner reading "INSTITUTION SLOGAN HERE" with orange "ESTABLISHED: 0000" text inside the ring.

This is a direct match for the required Alimzy badge: top arc "ALIMZY INTERNATIONAL SCHOOL", inner bottom "ESTABLISHED: 2026", ribbon "WE DON'T GIVE UP HERE".

---

## 11. Proposed batch plan and recommended prompt adjustments

### Batch 1 — hygiene & security (as specified)
Remove tracked `.env`, `db.sqlite3`, `staticfiles/`, `.idea/`; expand `.gitignore`; split settings into `base/dev/prod`; env-driven `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL` (add `dj-database-url`), CORS/CSRF; production security flags; `.env.example`; ruff + pre-commit; runtime/dev dependency groups; multi-stage non-root Dockerfile + healthcheck; working compose; README; JWT rotation/blacklist + throttling + password validators; `/api/health/`.

**Additions I recommend:** `django-cors-headers`, `dj-database-url`, `django-filter` (needed in Batch 2 anyway), `drf-spectacular` (see below), and a `pytest`/`factory_boy` dev group prepared for Batch 3. Also add `design/` to git (binaries) so the brand assets survive clones.

### Batch 2 — domain & API
**Recommendation:** build a new school domain rather than contorting the university models. Concretely: keep `core.User` and email login; introduce `SchoolProfile`, `AcademicYear`, `Term`, `SchoolClass`, `ClassArm`, `Subject`, `TeacherAssignment`, `StudentEnrollment`, `AssessmentComponent`, `GradeScale`/`GradeBand`, `Result`, `ClassResult` (publish/lock), `Attendance`, `ScoreAudit`, `ResultVerification`. Migrate `role="staff"` → `teacher`; add `parent` only if you want it.

**Legacy compatibility:** the current Department/Course/Level endpoints are university-shaped and unused by the target UI. I recommend **replacing** them with the school API and keeping thin read-only compatibility shims only if you have clients depending on them. This is a deliberate breaking change; please confirm.

**Choices to confirm:**
- OpenAPI: **drf-spectacular** (OpenAPI 3.1, actively maintained, Django 6 compatible) instead of drf-yasg (unmaintained, OpenAPI 2). Recommended.
- PDF: **WeasyPrint** (HTML/CSS templates, easiest to match the report-card design) over ReportLab. Requires Pango/Cairo system libs (not installed yet).
- Grading: Nigerian WAEC-style `A1–F9` or simpler `A–F`? CA/exam split (e.g. CA 40 / Exam 60)? CA components (test 1, test 2, assignment, project)?
- Timezone `Africa/Lagos`; currency/locale not needed for results but useful for settings.
- Logo font: **Montserrat** (SIL OFL 1.1) — confirm; I will convert text to outlines in exported SVGs.
- Email provider for password reset (SMTP/console in dev).

### Batch 3 — tests & CI
pytest + pytest-django + factory_boy; ≥80% coverage on `results`, `academics`, `account`; GitHub Actions on `master` with Postgres service, lint, migration check, Docker build. Replace the current `main`-only ECR workflow (or keep ECR as an optional deploy job).

### Batch 4 — frontend foundation
React + Vite + TS + Tailwind + Router + TanStack Query + RHF/Zod + Axios refresh interceptor. **Redux Toolkit is not needed:** auth/session can live in a small React context + TanStack Query cache, which avoids duplicate state. I will justify this in `DESIGN_NOTES.md` and wait for approval before UI work. Need the image/PDF toolchain installed for logo export.

### Batch 5 — screens
Admin, teacher, student and public verification screens as specified, with loading/empty/error states, pagination/search, Playwright E2E for the three main flows.

### Batch 6 — deployment
Compare Render/Railway/Fly.io, then implement the chosen target. Plan for S3-compatible/Cloudinary media (report-card logos/signatures) because free host disks are ephemeral.

---

## 12. Decisions I need from you before Batch 1/2

1. **Rotate secrets now:** the committed `SECRET_KEY` and Postgres password must be considered compromised. I cannot rotate them for you. Confirm you will rotate them; I will scrub them from the working tree in Batch 1 (history rewrite is a separate, explicit decision).
2. **Legacy domain:** may I replace Department/Course/Level/Semester with the school model (Year/Term/Class/Arm/Subject/Enrollment), keeping only compatibility shims if needed? (Recommended: yes.)
3. **Grading scheme:** WAEC `A1–F9` or `A–F`? What CA/exam weights and CA components?
4. **OpenAPI:** approve **drf-spectacular** (recommended) or keep drf-yasg?
5. **PDF engine:** approve **WeasyPrint** (recommended) or ReportLab?
6. **Parent role:** include it now or defer?
7. **Logo font:** Montserrat (OFL) acceptable? Any font preference?
8. **Email:** which provider/SMTP should password-reset use in production? (Console backend in dev is fine.)
9. **Demo credentials:** should `seed_demo` read passwords from env (recommended) or generate random ones and print them?
10. **Design assets in git:** may I commit the ~3 MB `design/` folder in Batch 1 so the screenshots/logo are versioned?

---

## 13. Branch status

- Branch: `batch-0-audit`
- Changes: `AUDIT.md`, `PROGRESS.md` only
- No code, settings, migrations, or tracked assets changed
- Ready for review/merge after you answer the decisions above
