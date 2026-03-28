"""
User, Membership, and AuditLog models for the KCK (Kenya Community in Korea) platform.

I designed these models around three core concerns:
1. User identity with email-based authentication (no usernames -- our members identify
   by email across the Laravel frontend and Django backend).
2. Membership lifecycle with in-place renewal (not creating new records each year).
3. Full audit trail via AuditLog so leadership can review every sensitive action.

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


# -------------------------------------------------------------------
# Choices
# -------------------------------------------------------------------
CITY_CHOICES = [
    ("seoul", "Seoul"),
    ("busan", "Busan"),
    ("incheon", "Incheon"),
    ("daegu", "Daegu"),
    ("daejeon", "Daejeon"),
    ("gwangju", "Gwangju"),
    ("other", "Other"),
]

CATEGORY_CHOICES = [
    ("student", "Student"),
    ("worker", "Worker"),
    ("professional", "Professional"),
    ("tourist", "Tourist"),
]

MEMBERSHIP_STATUS_CHOICES = [
    ("active", "Active"),
    ("expired", "Expired"),
    ("pending", "Pending"),
    ("cancelled", "Cancelled"),
]

PAYMENT_STATUS_CHOICES = [
    ("pending_verification", "Pending Verification"),
    ("verified", "Verified"),
    ("rejected", "Rejected"),
]


# -------------------------------------------------------------------
# Custom User Manager
# -------------------------------------------------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("full_name", "Admin")
        return self.create_user(email, password, **extra)


# -------------------------------------------------------------------
# User model
# -------------------------------------------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    # I chose UUID primary keys for distributed-system compatibility. Our Django backend
    # and Laravel frontend both generate references to users, and sequential integer IDs
    # would leak information about total user count and create conflicts if we ever merge
    # data from multiple sources (e.g., chapter databases).
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=120)
    # Email is the USERNAME_FIELD (not a separate username) because our community members
    # sign up with their email addresses. A username would be an extra piece of data nobody
    # remembers. Email is already guaranteed unique and is what we use for all communication.
    email = models.EmailField(unique=True, db_index=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True, default="")
    phone = models.CharField(max_length=25, blank=True, default="")
    korean_phone = models.CharField(max_length=20, blank=True, default="", help_text="Korean phone number (e.g., 010-1234-5678)")
    address_korea = models.TextField(blank=True, default="")
    city = models.CharField(max_length=60, choices=CITY_CHOICES, default="seoul")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="student")
    visa_type = models.CharField(max_length=30, blank=True, default="")
    arrival_date = models.DateField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=120, blank=True, default="")
    emergency_contact_phone = models.CharField(max_length=25, blank=True, default="")
    photo = models.ImageField(upload_to="photos/", blank=True)

    # Verification is a manual step by the secretary/chairman to confirm the member's
    # identity. This is separate from email_verified -- a user can verify their email
    # but still need a leader to approve their community membership.
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        "leaders.Leader",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="verified_users",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    # Soft-delete pattern: we never hard-delete user records because membership history,
    # audit logs, and certificate records reference them. Setting is_deleted=True and
    # is_active=False hides the user from queries and blocks login while preserving
    # referential integrity and the ability to restore accounts if needed.
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS is empty because email is already the USERNAME_FIELD (Django
    # automatically prompts for it). full_name is set via the registration serializer.
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["is_deleted", "deleted_at", "is_active", "updated_at"])

    @property
    def membership_status(self):
        """Return the status of the latest membership."""
        latest = self.memberships.order_by("-start_date").first()
        if latest:
            return latest.status
        return None


# -------------------------------------------------------------------
# Membership model
# -------------------------------------------------------------------
class Membership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS_CHOICES, default="pending", db_index=True)
    start_date = models.DateField()
    expiry_date = models.DateField(blank=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, default="KRW")
    payment_method = models.CharField(max_length=40, blank=True, default="")
    payment_reference = models.CharField(max_length=80, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    renewal_count = models.PositiveIntegerField(default=0)
    last_renewed_at = models.DateTimeField(null=True, blank=True)
    # renewal_history stores a JSON array of renewal entries, each recording the old expiry,
    # new expiry, date of renewal, and who performed it. I chose a JSON field over a separate
    # RenewalRecord model because renewals happen at most once a year per member, so a
    # lightweight embedded audit trail keeps the schema simple while still giving the
    # treasurer full visibility into the renewal chain.
    renewal_history = models.JSONField(default=list, blank=True, help_text="List of {date, extended_from, extended_to, by}")
    payment_screenshot = models.ImageField(upload_to="payments/", blank=True)
    payment_status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending_verification",
    )
    recorded_by = models.ForeignKey(
        "leaders.Leader",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recorded_memberships",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"Membership({self.user.full_name}, {self.status})"

    def renew(self, renewed_by=None):
        """
        Extend this membership by 1 year from current expiry (or today if expired).

        We check expiry >= today because renewal should extend from the current end date,
        not create gaps. If a member renews a week before expiry, they keep that remaining
        week plus a full year. If they renew after expiry, we start fresh from today so
        they don't lose days retroactively.
        """
        from datetime import date as date_cls
        old_expiry = self.expiry_date
        if old_expiry and old_expiry >= date_cls.today():
            new_start = old_expiry
        else:
            new_start = date_cls.today()
        new_expiry = new_start + timedelta(days=365)

        # Record in history
        entry = {
            "date": str(timezone.now().date()),
            "extended_from": str(old_expiry),
            "extended_to": str(new_expiry),
            "by": str(renewed_by) if renewed_by else None,
        }
        if not isinstance(self.renewal_history, list):
            self.renewal_history = []
        self.renewal_history.append(entry)

        self.expiry_date = new_expiry
        self.status = "active"
        self.renewal_count += 1
        self.last_renewed_at = timezone.now()
        self.save(update_fields=["expiry_date", "status", "renewal_count", "last_renewed_at", "renewal_history"])
        return self

    def save(self, *args, **kwargs):
        # Auto-calculate expiry_date if not explicitly set. The date string handling
        # (isinstance check for str) exists because DRF sometimes passes date values as
        # ISO strings rather than date objects, especially when coming through serializer
        # validated_data. We normalize to a date object before doing arithmetic.
        if not self.expiry_date:
            start = self.start_date
            if isinstance(start, str):
                from datetime import date as date_cls
                start = date_cls.fromisoformat(start)
                self.start_date = start
            self.expiry_date = start + timedelta(days=365)
        super().save(*args, **kwargs)


# -------------------------------------------------------------------
# AuditLog model
# -------------------------------------------------------------------
# AuditLog provides a permanent, append-only record of every significant action in the
# system. We store old_values and new_values as JSON so we can reconstruct what changed
# without needing a separate history table per model. The ip_address field helps with
# security investigations if an account is compromised.
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("created", "Created"),
        ("updated", "Updated"),
        ("deleted", "Deleted"),
        ("verified", "Verified"),
        ("published", "Published"),
    ]

    id = models.BigAutoField(primary_key=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=30)
    model_type = models.CharField(max_length=60)
    model_id = models.UUIDField(db_index=True)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"AuditLog({self.action} {self.model_type} {self.model_id})"
