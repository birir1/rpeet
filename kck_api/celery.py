"""
Celery configuration for the KCK API project.
Author: Meshack Tirop

I configured Celery with Redis as the broker (set in Django settings) and
autodiscover_tasks to pick up tasks.py from every installed app automatically.
"""
import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kck_api.settings.base")

app = Celery("kck_api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Beat schedule -- I run membership expiry at 1:00 AM KST daily so that
# expired memberships are cleaned up overnight before members see stale
# "active" statuses in the morning. The analytics cache refreshes every 15
# minutes as a compromise between dashboard freshness and database load.
app.conf.beat_schedule = {
    "expire-memberships-daily": {
        "task": "apps.users.tasks.expire_memberships_task",
        "schedule": crontab(hour=1, minute=0),
    },
    "refresh-analytics-cache": {
        "task": "apps.analytics.tasks.refresh_analytics_cache",
        "schedule": crontab(minute="*/15"),
    },
}
