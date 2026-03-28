"""
Event, EventAttendee, and EventPhoto models for KCK community events.
Author: Meshack Tirop

I structured events around three models: Event holds the core data with
auto-generated slugs for clean URLs, EventAttendee tracks participation
(supporting both registered platform users and walk-in guests), and EventPhoto
provides a gallery system with sort ordering for post-event photo sharing.
"""
import uuid

from django.db import models
from django.utils.text import slugify


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    title = models.CharField(max_length=250)
    body = models.TextField(blank=True, default="")
    excerpt = models.CharField(max_length=300, blank=True, default="")
    event_date = models.DateField()
    location = models.CharField(max_length=250, blank=True, default="")
    cover_image = models.ImageField(upload_to="photos/events/", blank=True)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "leaders.Leader",
        on_delete=models.PROTECT,
        related_name="events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-event_date"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # I auto-generate slugs from the event title on first save so that
        # event URLs are human-readable (e.g., /events/annual-gala-2026/).
        # The while-loop appends a numeric suffix if a slug collision occurs,
        # which is common with similarly-named recurring events.
        if not self.slug:
            base = slugify(self.title)[:140]
            slug = base
            counter = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class EventAttendee(models.Model):
    """Tracks event participation for both registered and non-registered users.

    I designed this with an optional `user` FK so that leaders can record
    attendance for walk-in guests who aren't registered on the platform. The
    `name` field is always populated regardless -- for registered users it's
    copied from their profile, for guests it's entered manually. This lets us
    generate complete attendance lists without requiring everyone to sign up.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=120)  # For non-registered attendees
    email = models.EmailField(blank=True)
    attended = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} @ {self.event.title}"


class EventPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="photos")
    photo = models.ImageField(upload_to="photos/events/")
    caption = models.CharField(max_length=200, blank=True, default="")
    sort_order = models.SmallIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        "leaders.Leader",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_photos",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self):
        return f"Photo for {self.event.title}"
