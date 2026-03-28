"""
Views for Certificate endpoints.

Certificates are generated asynchronously via Celery tasks. The create endpoint
immediately returns while the image/PDF generation happens in the background,
and the frontend polls the status endpoint to know when the files are ready.

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
from django.http import FileResponse, Http404
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.common.audit import log_action
from apps.common.pagination import KCKPagination
from apps.common.permissions import IsAnyLeader

from .models import Certificate
from .serializers import (
    CertificateCreateSerializer,
    CertificateDetailSerializer,
    CertificateListSerializer,
    CertificateVerifySerializer,
)
from .tasks import generate_cert_image_task, generate_cert_pdf_task, generate_qr_task


class CertificateListView(generics.ListAPIView):
    """GET /kck/certs/"""
    serializer_class = CertificateListSerializer
    permission_classes = [IsAnyLeader]
    pagination_class = KCKPagination

    def get_queryset(self):
        return Certificate.objects.select_related("issued_by__user").all()


class CertificateCreateView(generics.CreateAPIView):
    """POST /kck/certs/"""
    serializer_class = CertificateCreateSerializer
    permission_classes = [IsAnyLeader]

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.status = "generating"
        instance.save(update_fields=["status"])
        log_action(
            actor=self.request.user,
            action="created",
            model_type="Certificate",
            model_id=instance.id,
            new_values={"cert_number": instance.cert_number, "recipient": instance.recipient_name},
            request=self.request,
        )
        # Dispatch the image/PDF generation as an async Celery task via .delay() so the
        # HTTP response returns immediately. Certificate generation involves Pillow image
        # rendering and PDF conversion, which can take 2-5 seconds -- too slow for a
        # synchronous request. The frontend polls CertificateStatusView to check progress.
        generate_cert_image_task.delay(str(instance.id))


class CertificateDetailView(generics.RetrieveAPIView):
    """GET /kck/certs/{id}/"""
    serializer_class = CertificateDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    queryset = Certificate.objects.select_related("issued_by__user")


class CertificatePDFView(views.APIView):
    """GET /kck/certs/{id}/pdf/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            cert = Certificate.objects.get(id=id)
        except Certificate.DoesNotExist:
            raise Http404
        if not cert.pdf_file:
            return Response({"detail": "PDF not yet generated."}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(cert.pdf_file.open("rb"), content_type="application/pdf")


class CertificateImageView(views.APIView):
    """GET /kck/certs/{id}/image/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            cert = Certificate.objects.get(id=id)
        except Certificate.DoesNotExist:
            raise Http404
        if not cert.image_file:
            return Response({"detail": "Image not yet generated."}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(cert.image_file.open("rb"), content_type="image/png")


class CertificateVerifyView(views.APIView):
    """GET /kck/certs/verify/{cert_number}/"""
    permission_classes = [AllowAny]

    def get(self, request, cert_number):
        try:
            cert = Certificate.objects.select_related("issued_by__user").get(cert_number=cert_number)
        except Certificate.DoesNotExist:
            return Response(
                {"detail": "Certificate not found.", "valid": False},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = CertificateVerifySerializer(cert).data
        data["valid"] = True
        return Response(data)


class CertificateStatusView(views.APIView):
    """
    GET /kck/certs/{id}/status/

    Polling endpoint for the frontend to check if certificate generation is complete.
    The frontend calls this every few seconds after creating a certificate until
    status changes from "generating" to "published" (or "failed"), at which point
    the image and PDF download links become available.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            cert = Certificate.objects.get(id=id)
        except Certificate.DoesNotExist:
            raise Http404
        return Response({
            'status': cert.status,
            'has_image': bool(cert.image_file),
            'has_pdf': bool(cert.pdf_file),
            'cert_number': cert.cert_number,
        })


class CertificateMineView(generics.ListAPIView):
    """GET /kck/certs/mine/ - certificates for the current user."""
    serializer_class = CertificateListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(
            recipient_user=self.request.user
        ).select_related("issued_by__user")
