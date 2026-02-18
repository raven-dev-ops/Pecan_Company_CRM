"""Django settings for local development.

This project is intentionally minimal:
- Default DB is SQLite (file-based, no server required).
- Azure / legacy integrations are stubbed behind feature flags.

To run locally:
1) Copy .env.example -> .env
2) python -m pip install -r requirements.txt
3) python manage.py migrate
4) python manage.py runserver
"""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

# Optional: load environment variables from ./ .env (requires python-dotenv)
_env_path = BASE_DIR / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(_env_path)
    except Exception:
        # If python-dotenv isn't installed, we simply don't load .env.
        pass


# --- Core settings ---
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"

_allowed_hosts_raw = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_raw.split(",") if h.strip()]


# --- Application definition ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.apps.CoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# --- Database ---
# Default: SQLite (file-based SQL database) for local development.
# Later: switch DATABASE_ENGINE=mssql and fill MSSQL_* values to connect to Azure SQL.
DATABASE_ENGINE = os.getenv("DATABASE_ENGINE", "sqlite").lower().strip()

if DATABASE_ENGINE == "sqlite":
    sqlite_path = os.getenv("SQLITE_PATH")
    if not sqlite_path:
        sqlite_path = str(BASE_DIR / "db.sqlite3")

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": sqlite_path,
        }
    }

elif DATABASE_ENGINE == "mssql":
    # Requires installing mssql-django + pyodbc and an appropriate ODBC driver.
    # We keep it here as a placeholder so the project structure is ready.
    DATABASES = {
        "default": {
            "ENGINE": "mssql",
            "NAME": os.getenv("MSSQL_NAME", ""),
            "HOST": os.getenv("MSSQL_HOST", ""),
            "PORT": os.getenv("MSSQL_PORT", ""),
            "USER": os.getenv("MSSQL_USER", ""),
            "PASSWORD": os.getenv("MSSQL_PASSWORD", ""),
            "OPTIONS": {
                "driver": os.getenv("MSSQL_DRIVER", "ODBC Driver 18 for SQL Server"),
            },
        }
    }

else:
    raise RuntimeError(f"Unsupported DATABASE_ENGINE={DATABASE_ENGINE!r}")


# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- Internationalization ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# --- Static files ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


# --- Defaults ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Feature flags: integrations (stubbed for now) ---
AZURE_ENABLED = os.getenv("AZURE_ENABLED", "0") == "1"
LEGACY_ENABLED = os.getenv("LEGACY_ENABLED", "0") == "1"