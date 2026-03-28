from django.contrib import admin

from .models import Leader


@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "is_active", "appointed_at")
    list_filter = ("role", "is_active")
