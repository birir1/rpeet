"""
Serializers for User and Membership models.

These serializers handle validation, transformation, and access control for user and
membership data flowing between the API and the database. I maintain separate serializers
for list vs. detail views to minimize payload size on list endpoints, and separate
create vs. update serializers for memberships to enforce immutability of certain fields
(e.g., you cannot change the owner of a membership after creation).

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
from datetime import timedelta

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import Membership, User


class UserRegistrationSerializer(serializers.ModelSerializer):
    # write_only=True ensures the password hash is never included in API responses.
    # Even though we store hashed passwords, exposing the hash would still be a
    # security risk (offline brute-force attacks).
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "password",
            "phone",
            "korean_phone",
            "city",
            "category",
            "visa_type",
            "arrival_date",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]
        read_only_fields = ["id"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    """
    Used for listing users.
    """
    membership_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "city",
            "category",
            "is_verified",
            "membership_status",
            "created_at",
        ]

    def get_membership_status(self, obj):
        return obj.membership_status


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Full detail view of a user.
    """
    membership_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "korean_phone",
            "address_korea",
            "city",
            "category",
            "visa_type",
            "arrival_date",
            "emergency_contact_name",
            "emergency_contact_phone",
            "photo",
            "is_verified",
            "verified_at",
            "membership_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_verified",
            "verified_at",
            "created_at",
            "updated_at",
        ]

    def get_membership_status(self, obj):
        return obj.membership_status

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Fallback to default avatar if no photo uploaded
        if not data.get("photo"):
            request = self.context.get("request")
            default = "/static/images/default-avatar.png"
            data["photo"] = request.build_absolute_uri(default) if request else default
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "full_name",
            "phone",
            "korean_phone",
            "address_korea",
            "city",
            "category",
            "visa_type",
            "arrival_date",
            "emergency_contact_name",
            "emergency_contact_phone",
            "photo",
        ]


class MembershipSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "user",
            "user_name",
            "status",
            "start_date",
            "expiry_date",
            "fee_amount",
            "currency",
            "payment_method",
            "payment_reference",
            "notes",
            "payment_screenshot",
            "payment_status",
            "renewal_count",
            "last_renewed_at",
            "recorded_by",
            "created_at",
        ]
        read_only_fields = ["id", "expiry_date", "recorded_by", "created_at"]
        extra_kwargs = {
            "user": {"required": False},  # Not required on update
        }

    def validate(self, attrs):
        # user is required on create
        if not self.instance and not attrs.get("user"):
            raise serializers.ValidationError({"user": "This field is required when creating a membership."})
        return attrs

    def to_representation(self, instance):
        # Convert UUID fields to strings in the output. DRF's default PrimaryKeyRelatedField
        # serializes UUIDs as UUID objects, which causes issues when the frontend (Laravel/JS)
        # expects plain string UUIDs. This explicit str() conversion ensures consistent
        # JSON output across all UUID foreign key fields.
        data = super().to_representation(instance)
        data['user'] = str(data['user']) if data.get('user') else None
        data['recorded_by'] = str(data['recorded_by']) if data.get('recorded_by') else None
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request.user, "leader"):
            validated_data["recorded_by"] = request.user.leader
        start = validated_data.get("start_date")
        if start:
            validated_data["expiry_date"] = start + timedelta(days=365)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        start = validated_data.get("start_date", instance.start_date)
        if "start_date" in validated_data:
            validated_data["expiry_date"] = start + timedelta(days=365)
        return super().update(instance, validated_data)


class MembershipUpdateSerializer(serializers.ModelSerializer):
    """Used for PUT/PATCH - user field is excluded (cannot change membership owner)."""
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "user",
            "user_name",
            "status",
            "start_date",
            "expiry_date",
            "fee_amount",
            "currency",
            "payment_method",
            "payment_reference",
            "notes",
            "payment_screenshot",
            "payment_status",
            "renewal_count",
            "last_renewed_at",
            "recorded_by",
            "created_at",
        ]
        read_only_fields = ["id", "user", "expiry_date", "recorded_by", "created_at"]

    def update(self, instance, validated_data):
        start = validated_data.get("start_date", instance.start_date)
        if "start_date" in validated_data:
            validated_data["expiry_date"] = start + timedelta(days=365)
        return super().update(instance, validated_data)


class MembershipRequestSerializer(serializers.Serializer):
    """Serializer for public membership request by authenticated users."""
    payment_method = serializers.CharField(max_length=40, required=False, default="")
    payment_reference = serializers.CharField(max_length=80, required=False, default="")
    notes = serializers.CharField(required=False, default="")
    payment_screenshot = serializers.ImageField(required=False)


class MeSerializer(serializers.ModelSerializer):
    """Serializer for the /auth/me/ endpoint."""
    membership_status = serializers.SerializerMethodField()
    is_leader = serializers.SerializerMethodField()
    leader_role = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "korean_phone",
            "city",
            "category",
            "photo",
            "is_verified",
            "email_verified",
            "membership_status",
            "is_leader",
            "leader_role",
        ]

    def get_photo(self, obj):
        request = self.context.get("request")
        if obj.photo:
            return request.build_absolute_uri(obj.photo.url) if request else obj.photo.url
        default = "/static/images/default-avatar.png"
        return request.build_absolute_uri(default) if request else default

    def get_membership_status(self, obj):
        return obj.membership_status

    def get_is_leader(self, obj):
        try:
            return obj.leader.is_active
        except Exception:
            return False

    def get_leader_role(self, obj):
        try:
            leader = obj.leader
            if leader.is_active:
                return leader.role
        except Exception:
            pass
        return None
