"""
Communication and Announcement models for the KCK platform.
Author: Meshack Tirop

I designed Communications as the formal document pipeline -- each one gets a
unique reference number and goes through async Celery rendering to produce
official letterhead PDFs. Announcements are the lighter-weight counterpart:
simple rich-text posts that don't need document generation.
"""
import uuid

from django.db import models, transaction
from django.db.utils import IntegrityError
from django.utils import timezone

COMM_CATEGORY_CHOICES = [
    ("general", "General"),
    ("urgent", "Urgent"),
    ("welfare", "Welfare"),
    ("events", "Events"),
    ("emergency", "Emergency"),
]

COMM_AUDIENCE_CHOICES = [
    ("all", "All"),
    ("members_only", "Members Only"),
    ("city", "City"),
    ("category_group", "Category Group"),
]

COMM_STATUS_CHOICES = [
    ("processing", "Processing"),
    ("published", "Published"),
    ("draft", "Draft"),
]


class Communication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_number = models.CharField(max_length=40, unique=True, blank=True)
    subject = models.CharField(max_length=250)
    body = models.TextField()
    category = models.CharField(max_length=30, choices=COMM_CATEGORY_CHOICES, default="general")
    audience = models.CharField(max_length=30, choices=COMM_AUDIENCE_CHOICES, default="all")
    audience_filter = models.CharField(max_length=80, blank=True, default="")
    sender = models.ForeignKey(
        "leaders.Leader",
        on_delete=models.PROTECT,
        related_name="communications",
    )
    status = models.CharField(max_length=20, choices=COMM_STATUS_CHOICES, default="processing", db_index=True)
    pdf_file = models.FileField(upload_to="communications/", blank=True)
    image_file = models.ImageField(upload_to="communications/", blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference_number}: {self.subject}"

    def save(self, *args, **kwargs):
        # I auto-generate reference numbers on first save using an atomic
        # transaction with select_for_update to prevent two concurrent saves
        # from getting the same sequence number. The retry loop (up to 5
        # attempts) handles the rare race condition where two requests count
        # the same number of rows before either commits -- the unique constraint
        # on reference_number catches the collision and we simply retry with
        # the updated count.
        if not self.reference_number:
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    with transaction.atomic():
                        self.reference_number = self._generate_reference()
                        super().save(*args, **kwargs)
                    return
                except IntegrityError:
                    if attempt == max_retries - 1:
                        raise
                    self.reference_number = ""
        else:
            super().save(*args, **kwargs)

    @staticmethod
    def _generate_reference():
        # Format: KCK/YEAR/001 -- I chose this format to match the official
        # KCK paper filing system. The year resets the counter annually so
        # numbers stay short, and the 3-digit zero-padded sequence makes
        # references sortable and easy to cite in meetings.
        now = timezone.now()
        year = now.year
        count = (
            Communication.objects.select_for_update()
            .filter(created_at__year=year)
            .count()
            + 1
        )
        return f"KCK/{year}/{count:03d}"


ANNOUNCEMENT_CATEGORY_CHOICES = [
    ("general", "General"),
    ("condolence", "Condolence"),
    ("event", "Upcoming Event"),
    ("welfare", "Welfare"),
    ("notice", "Notice"),
    ("celebration", "Celebration"),
]


class Announcement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    body = models.TextField()  # Rich HTML from CKEditor
    category = models.CharField(
        max_length=30,
        choices=ANNOUNCEMENT_CATEGORY_CHOICES,
        default="general",
    )
    is_published = models.BooleanField(default=True)
    cover_image = models.ImageField(upload_to="announcements/", blank=True)
    author = models.ForeignKey(
        "leaders.Leader",
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
