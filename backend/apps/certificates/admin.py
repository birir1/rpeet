from django.contrib import admin

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("cert_number", "recipient_name", "cert_type", "issued_at")
    list_filter = ("cert_type",)
    search_fields = ("cert_number", "recipient_name")
