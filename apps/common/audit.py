"""
Audit-logging helpers for the KCK platform.

Every Create, Update, Delete, Verify, and Publish operation should call log_action().
This provides a centralized audit trail that the chairman can review to see who did
what and when. I chose a single AuditLog table (in users/models.py) with a generic
model_type + model_id approach rather than per-model history tables because it keeps
the audit infrastructure simple and queryable -- you can filter by actor, by model type,
or by action type in a single query.

The IP address is captured for security investigations (e.g., detecting if a compromised
account is being accessed from an unusual location).

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
from django.utils import timezone


def get_client_ip(request):
    """Extract the client IP from the request."""
    if request is None:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_action(
    *,
    actor,
    action,
    model_type,
    model_id,
    old_values=None,
    new_values=None,
    request=None,
):
    """
    Create an AuditLog entry.  Import here to avoid circular imports.
    """
    from apps.users.models import AuditLog

    AuditLog.objects.create(
        actor=actor if (actor and actor.is_authenticated) else None,
        action=action,
        model_type=model_type,
        model_id=model_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=get_client_ip(request),
        created_at=timezone.now(),
    )
