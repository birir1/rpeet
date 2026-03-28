"""
Serializers for Event, EventPhoto, and EventAttendee models.
Author: Meshack Tirop

I use separate list/detail serializers for events to keep list responses lean
(no body or nested photos) while providing full data on detail views. The
BatchAttendeeInputSerializer supports bulk attendance recording so leaders can
submit a full attendance sheet in one API call rather than one request per person.
"""
from rest_framework import serializers

from .models import Event, EventAttendee, EventPhoto


class EventPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPhoto
        fields = ["id", "photo", "caption", "sort_order", "created_at"]
        read_only_fields = ["id", "created_at"]


class EventListSerializer(serializers.ModelSerializer):
    """List serializer: excludes body for performance."""
    created_by_name = serializers.CharField(source="created_by.user.full_name", read_only=True)
    photo_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "slug",
            "title",
            "excerpt",
            "event_date",
            "location",
            "cover_image",
            "is_published",
            "created_by_name",
            "photo_count",
            "created_at",
        ]

    def get_photo_count(self, obj):
        return obj.photos.count()


class EventDetailSerializer(serializers.ModelSerializer):
    """Detail serializer: includes body and photos."""
    created_by_name = serializers.CharField(source="created_by.user.full_name", read_only=True)
    photos = EventPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "slug",
            "title",
            "body",
            "excerpt",
            "event_date",
            "location",
            "cover_image",
            "is_published",
            "created_by_name",
            "photos",
            "created_at",
            "updated_at",
        ]


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "body",
            "excerpt",
            "event_date",
            "location",
            "cover_image",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["created_by"] = request.user.leader
        return super().create(validated_data)


class EventPhotoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPhoto
        fields = ["id", "photo", "caption", "sort_order"]
        read_only_fields = ["id"]


class EventAttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAttendee
        fields = ["id", "name", "email", "user_id", "attended", "created_at"]
        read_only_fields = ["id", "created_at"]


class EventAttendeeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAttendee
        fields = ["id", "name", "email", "user_id", "attended", "created_at"]


class BatchAttendeeInputSerializer(serializers.Serializer):
    attendees = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
    )

    def validate_attendees(self, value):
        for item in value:
            if "name" not in item or not item["name"]:
                raise serializers.ValidationError("Each attendee must have a 'name'.")
        return value
