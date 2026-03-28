from django.contrib import admin

from .models import Communication


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ("reference_number", "subject", "category", "status", "created_at")
    list_filter = ("category", "status", "audience")
    search_fields = ("reference_number", "subject")
