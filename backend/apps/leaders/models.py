"""
Leader and LeaderPermission models for the KCK leadership structure.

The leadership model represents the community's organizational hierarchy: Chairman,
Secretary, Treasurer, Welfare Officer, and Committee Members. Each leader is linked
to a User via a OneToOne relationship, and their permissions are stored in a separate
LeaderPermission model that gets auto-created with role-appropriate defaults.

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

LEADER_ROLE_CHOICES = [
    ("chairman", "Chairman"),
    ("secretary", "Secretary"),
    ("treasurer", "Treasurer"),
    ("welfare", "Welfare"),
    ("committee", "Committee"),
]

# Default permission mappings per role
ROLE_DEFAULT_PERMISSIONS = {
    "chairman": {
        "can_manage_users": True,
        "can_verify_users": True,
        "can_export_users": True,
        "can_manage_memberships": True,
        "can_view_financials": True,
        "can_send_communications": True,
        "can_issue_certificates": True,
        "can_manage_events": True,
        "can_manage_leaders": True,
        "can_view_analytics": True,
    },
    "secretary": {
        "can_manage_users": True,
        "can_verify_users": True,
        "can_export_users": True,
        "can_send_communications": True,
        "can_view_analytics": True,
    },
    "treasurer": {
        "can_manage_memberships": True,
        "can_view_financials": True,
        "can_send_communications": True,
    },
    "welfare": {
        "can_send_communications": True,
        "can_issue_certificates": True,
    },
    "committee": {
        "can_manage_events": True,
        "can_issue_certificates": True,
        "can_send_communications": True,
    },
}


class Leader(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="leader",
    )
    role = models.CharField(max_length=30, choices=LEADER_ROLE_CHOICES)
    title = models.CharField(max_length=100, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    signature = models.ImageField(upload_to="signatures/", blank=True)
    stamp = models.ImageField(upload_to="signatures/", blank=True)
    is_active = models.BooleanField(default=True)
    appointed_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="appointees",
    )
    appointed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["role", "-created_at"]
        constraints = [
            # This partial unique constraint ensures only ONE active leader per role
            # at any time. For example, there can only be one active chairman. When a
            # chairman steps down (is_active=False), a new one can be appointed without
            # violating the constraint. The old record is preserved for historical reference.
            # Without this constraint, we'd risk data integrity issues where two people
            # both claim to be the active treasurer.
            models.UniqueConstraint(
                fields=["role"],
                condition=models.Q(is_active=True),
                name="unique_active_leader_per_role",
            ),
        ]

    def __str__(self):
        return f"{self.user.full_name} ({self.get_role_display()})"


class LeaderPermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    leader = models.OneToOneField(Leader, on_delete=models.CASCADE, related_name='permissions')
    can_manage_users = models.BooleanField(default=False)
    can_verify_users = models.BooleanField(default=False)
    can_export_users = models.BooleanField(default=False)
    can_manage_memberships = models.BooleanField(default=False)
    can_view_financials = models.BooleanField(default=False)
    can_send_communications = models.BooleanField(default=False)
    can_issue_certificates = models.BooleanField(default=False)
    can_manage_events = models.BooleanField(default=False)
    can_manage_leaders = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Permissions for {self.leader}"


# This signal auto-creates a LeaderPermission record with role-appropriate defaults
# whenever a new Leader is created. This ensures every leader immediately has the
# correct permissions without requiring a separate API call. The chairman can later
# customize these permissions via the admin panel or the leader management API.
@receiver(post_save, sender=Leader)
def create_default_permissions(sender, instance, created, **kwargs):
    """Auto-create default permissions when a Leader is created."""
    if created:
        defaults = ROLE_DEFAULT_PERMISSIONS.get(instance.role, {})
        LeaderPermission.objects.create(leader=instance, **defaults)
