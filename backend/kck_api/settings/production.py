"""
Production settings for the KCK API project.

Overrides base.py for production deployment on our Linux server. All sensitive values
come from environment variables -- nothing secret is committed to the repo. This file
is activated by setting DJANGO_SETTINGS_MODULE=kck_api.settings.production.

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
import os

from .base import *  # noqa: F401, F403

DEBUG = False

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]

# -------------------------------------------------------------------
# Database - PostgreSQL in production
# -------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "kck"),
        "USER": os.environ.get("DB_USER", "kck"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        # CONN_MAX_AGE: keep database connections alive for 10 minutes (600 seconds)
        # instead of opening a new connection per request. This significantly reduces
        # connection overhead with PostgreSQL, especially under concurrent load from
        # multiple Gunicorn workers.
        "CONN_MAX_AGE": 600,
    }
}

# -------------------------------------------------------------------
# Security
# -------------------------------------------------------------------
# SECURE_SSL_REDIRECT forces all HTTP requests to HTTPS. Combined with HSTS headers
# (31536000 seconds = 1 year), browsers will remember to always use HTTPS for our
# domain. HSTS_PRELOAD allows us to submit to the HSTS preload list so browsers enforce
# HTTPS even on first visit. SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE ensure cookies
# are never sent over unencrypted connections.
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# -------------------------------------------------------------------
# CORS - tighten in production
# -------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")

# -------------------------------------------------------------------
# Celery - real broker in production
# -------------------------------------------------------------------
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False

# -------------------------------------------------------------------
# Static files
# -------------------------------------------------------------------
STATIC_ROOT = os.environ.get("STATIC_ROOT", "/var/www/kck/static/")
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", "/var/www/kck/media/")

KCK_BASE_URL = os.environ.get("KCK_BASE_URL", "https://kenyakorea.com")

# -------------------------------------------------------------------
# Email
# -------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@kenyakorea.com')

# -------------------------------------------------------------------
# Cache - Redis in production
# -------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
    }
}

# -------------------------------------------------------------------
# Rate Limiting (enabled in production)
# -------------------------------------------------------------------
RATELIMIT_ENABLE = True

# -------------------------------------------------------------------
# Sentry Error Tracking
# -------------------------------------------------------------------
# Sentry is initialized conditionally: only if SENTRY_DSN is set in the environment.
# This lets us deploy to staging without Sentry and only enable it in production.
# traces_sample_rate=0.1 means we sample 10% of requests for performance monitoring,
# which keeps costs manageable while still giving us visibility into slow endpoints.
import sentry_sdk
SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )
