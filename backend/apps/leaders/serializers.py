"""
Serializers for Leader and LeaderPermission models.
Author: Meshack Tirop

I split leader serializers by use case: LeaderListSerializer exposes public-safe
fields, LeaderCreateSerializer handles chairman-initiated appointments,
LeaderSelfUpdateSerializer lets leaders manage their own profiles (including
cross-model photo updates on the User), and LeaderPermissionSerializer manages
the granular permission flags.
"""
from rest_framework import serializers

from .models import Leader, LeaderPermission


class LeaderListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Leader
        fields = [
            "id",
            "full_name",
            "email",
            "role",
            "title",
            "bio",
            "is_active",
            "appointed_at",
            "photo",
        ]

    def get_photo(self, obj):
        request = self.context.get("request")
        if obj.user.photo:
            if request:
                return request.build_absolute_uri(obj.user.photo.url)
            return obj.user.photo.url
        # Fallback to default avatar
        default = "/static/images/default-avatar.png"
        if request:
            return request.build_absolute_uri(default)
        return default


class LeaderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leader
        fields = [
            "id",
            "user",
            "role",
            "title",
            "bio",
            "signature",
            "stamp",
        ]
        read_only_fields = ["id"]


class LeaderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leader
        fields = [
            "role",
            "title",
            "bio",
            "signature",
            "stamp",
            "is_active",
        ]


class LeaderSelfUpdateSerializer(serializers.ModelSerializer):
    """Leaders can update their own bio, title, photo, and signature."""
    photo = serializers.ImageField(source="user.photo", required=False)

    class Meta:
        model = Leader
        fields = [
            "title",
            "bio",
            "signature",
            "photo",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if "photo" in user_data:
            instance.user.photo = user_data["photo"]
            instance.user.save(update_fields=["photo", "updated_at"])
        return super().update(instance, validated_data)


class LeaderPermissionSerializer(serializers.ModelSerializer):
    leader_name = serializers.CharField(source="leader.user.full_name", read_only=True)
    leader_role = serializers.CharField(source="leader.role", read_only=True)

    class Meta:
        model = LeaderPermission
        fields = [
            "id",
            "leader",
            "leader_name",
            "leader_role",
            "can_manage_users",
            "can_verify_users",
            "can_export_users",
            "can_manage_memberships",
            "can_view_financials",
            "can_send_communications",
            "can_issue_certificates",
            "can_manage_events",
            "can_manage_leaders",
            "can_view_analytics",
            "updated_at",
            "updated_by",
        ]
        read_only_fields = ["id", "leader", "leader_name", "leader_role", "updated_at", "updated_by"]
