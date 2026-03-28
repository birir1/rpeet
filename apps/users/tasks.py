"""
Celery tasks for user lifecycle management.
Author: Meshack Tirop

I keep user-related async tasks here, separate from the views, so that
Celery Beat can invoke them on a schedule without importing the full
Django request/response machinery.
"""
from celery import shared_task
from django.utils import timezone


@shared_task
def expire_memberships_task():
    """Daily task: expire memberships past their expiry_date.

    I run this nightly via Celery Beat (configured in kck_api/celery.py at
    1:00 AM KST). It bulk-updates all active memberships whose expiry_date
    has passed, flipping their status to "expired" in a single query. This
    keeps the membership status accurate without requiring members to log in
    or leaders to manually revoke expired memberships.
    """
    from .models import Membership

    today = timezone.now().date()
    expired = Membership.objects.filter(
        status="active",
        expiry_date__lt=today,
    ).update(status="expired")
    return f"Expired {expired} memberships."


@shared_task
def send_notification_task(subject, body, recipient_emails):
    """Send email notification (stub for dev)."""
    # In production, use django.core.mail.send_mail
    return f"Would send '{subject}' to {len(recipient_emails)} recipients."
