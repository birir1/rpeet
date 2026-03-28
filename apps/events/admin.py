from django.contrib import admin

from .models import Event, EventPhoto


class EventPhotoInline(admin.TabularInline):
    model = EventPhoto
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_date", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [EventPhotoInline]


@admin.register(EventPhoto)
class EventPhotoAdmin(admin.ModelAdmin):
    list_display = ("event", "caption", "sort_order")
