"""
Celery tasks for the analytics app.
"""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def refresh_analytics_cache():
    """
    Refresh analytics cache every 15 minutes.
    In a production system, this would pre-compute and cache analytics
    data in Redis or a dedicated analytics table.
    """
    from apps.users.models import Membership, User

    total = User.objects.filter(is_deleted=False).count()
    active = Membership.objects.filter(status="active").count()
    logger.info("Analytics cache refreshed: %d users, %d active memberships", total, active)
    return {"total_users": total, "active_memberships": active}
