"""
Serializers for Communication and Announcement.
"""
import re

import bleach
from rest_framework import serializers

from .models import Announcement, Communication

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "ul", "ol", "li", "a", "h1", "h2", "h3",
    "h4", "h5", "h6", "blockquote", "pre", "code", "span", "div",
]
ALLOWED_ATTRS = {
    "a": ["href", "title", "target"],
    "span": ["style"],
    "div": ["style"],
}


class CommunicationListSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.user.full_name", read_only=True)

    class Meta:
        model = Communication
        fields = [
            "id",
            "reference_number",
            "subject",
            "category",
            "audience",
            "sender_name",
            "status",
            "published_at",
            "created_at",
        ]


class CommunicationDetailSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.user.full_name", read_only=True)

    class Meta:
        model = Communication
        fields = [
            "id",
            "reference_number",
            "subject",
            "body",
            "category",
            "audience",
            "audience_filter",
            "sender_name",
            "status",
            "pdf_file",
            "image_file",
            "published_at",
            "created_at",
        ]


class BulkEmailSerializer(serializers.Serializer):
    """Serializer for bulk email endpoint."""
    subject = serializers.CharField(max_length=250)
    body = serializers.CharField()
    recipient_filter = serializers.ChoiceField(
        choices=["all", "members_only", "by_city", "by_category", "custom"],
    )
    filter_value = serializers.CharField(required=False, default="", allow_blank=True)


class CommunicationCreateSerializer(serializers.ModelSerializer):
    audience_filter = serializers.CharField(required=False, default="", allow_blank=True, allow_null=True)

    class Meta:
        model = Communication
        fields = [
            "id",
            "subject",
            "body",
            "category",
            "audience",
            "audience_filter",
        ]
        read_only_fields = ["id"]

    def validate_audience_filter(self, value):
        # Convert null to empty string
        return value or ""

    def validate_body(self, value):
        return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["sender"] = request.user.leader
        return super().create(validated_data)


# ---------------------------------------------------------------------------
# Announcement serializers
# ---------------------------------------------------------------------------

def _strip_html(text: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    clean = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", clean).strip()


class AnnouncementListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.user.full_name", read_only=True, default="")
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "category",
            "author_name",
            "created_at",
            "excerpt",
        ]

    def get_excerpt(self, obj):
        return _strip_html(obj.body)[:200]


class AnnouncementDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.user.full_name", read_only=True, default="")

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "body",
            "category",
            "is_published",
            "cover_image",
            "author_name",
            "created_at",
            "updated_at",
        ]


class AnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "body",
            "category",
            "cover_image",
            "is_published",
        ]
        read_only_fields = ["id"]

    def validate_body(self, value):
        return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["author"] = request.user.leader
        return super().create(validated_data)
