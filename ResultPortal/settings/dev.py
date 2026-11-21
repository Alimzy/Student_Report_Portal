"""Local development settings.

Loads ``.env`` from the repository root when present. Safe defaults are used
for localhost only; never point ``DJANGO_SETTINGS_MODULE`` at this module in
production.
"""

from __future__ import annotations

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

from .base import *  # noqa: E402,F401,F403

DEBUG = env_bool("DEBUG", True)  # noqa: F405

if not SECRET_KEY:  # noqa: F405
    raise ImproperlyConfigured(
        "SECRET_KEY is not set. Copy .env.example to .env and set a strong value."
    )

ALLOWED_HOSTS = env_list(  # noqa: F405
    "ALLOWED_HOSTS", ["localhost", "127.0.0.1", "0.0.0.0"]
)

# Local development falls back to SQLite when no database URL is configured.
# Docker Compose and CI set DATABASE_URL explicitly.
if not DATABASES:  # noqa: F405
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# The manifest static storage requires collectstatic; use the plain storage
# for hot-reloading development servers.
STORAGES = {  # noqa: F405
    **STORAGES,  # noqa: F405
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

EMAIL_BACKEND = os.getenv(  # noqa: F405
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
