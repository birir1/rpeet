from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuditLog, Membership, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "full_name", "city", "category", "is_verified", "is_deleted")
    list_filter = ("city", "category", "is_verified", "is_deleted")
    search_fields = ("email", "full_name")
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": (
            "full_name", "phone", "korean_phone", "address_korea",
            "city", "category", "visa_type", "arrival_date",
            "emergency_contact_name", "emergency_contact_phone", "photo",
        )}),
        ("Verification", {"fields": ("is_verified", "verified_by", "verified_at")}),
        ("Status", {"fields": ("is_active", "is_staff", "is_superuser", "is_deleted", "deleted_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "password1", "password2"),
        }),
    )


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "start_date", "expiry_date", "fee_amount")
    list_filter = ("status",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "model_type", "model_id", "created_at")
    list_filter = ("action", "model_type")
    readonly_fields = ("actor", "action", "model_type", "model_id", "old_values", "new_values", "ip_address", "created_at")
