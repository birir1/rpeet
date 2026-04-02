"""
Base settings for the KCK API project -- local development configuration.

This file is the foundation for all environments. Production settings (production.py)
import everything from here and override what needs to change. I use SQLite locally
because it requires zero setup for new developers cloning the repo, and our dev data
volumes are small enough that SQLite performance is not a concern.

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-kck-dev-key-change-in-production-!@#$%^&*()",
)

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# -------------------------------------------------------------------
# Application definition
# -------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    # Local apps
    "apps.common",
    "apps.users",
    "apps.leaders",
    "apps.communications",
    "apps.certificates",
    "apps.events",
    "apps.analytics",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "kck_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "kck_api.wsgi.application"

# -------------------------------------------------------------------
# Database - SQLite for local dev
# -------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -------------------------------------------------------------------
# Custom user model
# -------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"

# -------------------------------------------------------------------
# Password validation
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------------------------
# Internationalization
# -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# Static / Media files
# -------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------------------------
# Django REST Framework
# -------------------------------------------------------------------
# We use a custom renderer (KCKRenderer) as the default so that every API response is
# wrapped in a consistent envelope: {success: true/false, data: ..., error: ...}.
# This makes it easier for the Laravel frontend to handle responses uniformly without
# checking status codes for every request. The frontend can always check response.success
# before accessing response.data.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "apps.common.renderers.KCKRenderer",
    ),
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.KCKPagination",
    "PAGE_SIZE": 25,
    "EXCEPTION_HANDLER": "apps.common.renderers.kck_exception_handler",
}

# -------------------------------------------------------------------
# Rate Limiting (disabled in dev/test, enabled in production)
# -------------------------------------------------------------------
# RATELIMIT_ENABLE is False in dev so that running tests and manual API testing
# from Postman/curl is not blocked by rate limits. Production overrides this to True.
# The rate limit decorators on views still exist but become no-ops when this is False.
RATELIMIT_ENABLE = False

# -------------------------------------------------------------------
# Simple JWT
# -------------------------------------------------------------------
# JWT token lifetimes: 24h access tokens in dev for convenience (no need to constantly
# refresh while testing). In production, this should be reduced to 15-30 minutes with
# the refresh token handling transparent re-authentication. The 7-day refresh token
# lifetime means users stay logged in for a week before needing to re-enter credentials.
# ROTATE_REFRESH_TOKENS + BLACKLIST_AFTER_ROTATION ensures that each refresh token is
# single-use, mitigating token theft scenarios.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

# -------------------------------------------------------------------
# Celery (eager for dev)
# -------------------------------------------------------------------
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
# CELERY_TASK_ALWAYS_EAGER = True runs all Celery tasks synchronously in the same
# process, so you don't need a running Redis server or Celery worker during development.
# Certificate generation, email sending, and PDF creation all happen inline.
# CELERY_TASK_EAGER_PROPAGATES ensures exceptions in tasks bubble up immediately
# rather than being silently swallowed, which is critical for debugging.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# -------------------------------------------------------------------
# KCK specific
# -------------------------------------------------------------------
KCK_BASE_URL = os.environ.get("KCK_BASE_URL", "http://127.0.0.1:8000")

# -------------------------------------------------------------------
# Cache
# -------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# -------------------------------------------------------------------
# Email - Console backend for development (prints to console)
# -------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "KCK <noreply@kenyakorea.com>"

# -------------------------------------------------------------------
# Logging - Console output for development
# -------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
