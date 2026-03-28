"""
Serializers for Certificate model.
Author: brian korir

I provide four serializers to match the different access patterns: a compact
list view, a full detail view (with file URLs), a create serializer that
sanitizes HTML input with bleach, and a minimal verify serializer for the
public certificate verification endpoint.
"""
import bleach
from rest_framework import serializers

from .models import Certificate


class CertificateListSerializer(serializers.ModelSerializer):
    issued_by_name = serializers.CharField(source="issued_by.user.full_name", read_only=True)

    class Meta:
        model = Certificate
        fields = [
            "id",
            "cert_number",
            "recipient_name",
            "cert_type",
            "issued_by_name",
            "verification_url",
            "status",
            "issued_at",
        ]


class CertificateDetailSerializer(serializers.ModelSerializer):
    issued_by_name = serializers.CharField(source="issued_by.user.full_name", read_only=True)

    class Meta:
        model = Certificate
        fields = [
            "id",
            "cert_number",
            "recipient_user",
            "recipient_name",
            "cert_type",
            "body",
            "event",
            "issued_by_name",
            "pdf_file",
            "image_file",
            "verification_url",
            "qr_code",
            "status",
            "issued_at",
        ]


class CertificateCreateSerializer(serializers.ModelSerializer):
    recipient_user = serializers.PrimaryKeyRelatedField(
        queryset=Certificate.recipient_user.field.related_model.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Certificate
        fields = [
            "id",
            "recipient_user",
            "recipient_name",
            "cert_type",
            "body",
            "event",
        ]
        read_only_fields = ["id"]

    def validate_body(self, value):
        return bleach.clean(
            value,
            tags=["p", "br", "strong", "em", "span"],
            attributes={"span": ["style"]},
            strip=True,
        )

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["issued_by"] = request.user.leader
        return super().create(validated_data)


class CertificateVerifySerializer(serializers.ModelSerializer):
    issued_by_name = serializers.CharField(source="issued_by.user.full_name", read_only=True)

    class Meta:
        model = Certificate
        fields = [
            "cert_number",
            "recipient_name",
            "cert_type",
            "issued_by_name",
            "issued_at",
            "verification_url",
        ]
