"""
Views for Communication and Announcement endpoints.

Communications are formal letters (with PDF/image generation), while Announcements are
simpler text-based posts with optional cover images. Both support CRUD operations for
leaders and public read access for published content.

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
import logging
from urllib.parse import quote

from django.http import FileResponse, Http404
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.common.audit import log_action
from apps.common.pagination import KCKPagination
from apps.common.permissions import IsAnyLeader

from .models import Announcement, Communication
from .serializers import (
    AnnouncementCreateSerializer,
    AnnouncementDetailSerializer,
    AnnouncementListSerializer,
    BulkEmailSerializer,
    CommunicationCreateSerializer,
    CommunicationDetailSerializer,
    CommunicationListSerializer,
)
from .tasks import generate_comm_pdf_task, generate_comm_image_task, send_bulk_email_task


class CommunicationListView(generics.ListAPIView):
    """GET /kck/comms/"""
    serializer_class = CommunicationListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = KCKPagination

    def get_queryset(self):
        return Communication.objects.select_related("sender__user").all()


logger = logging.getLogger("apps.communications")


class CommunicationCreateView(generics.CreateAPIView):
    """POST /kck/comms/create/"""
    serializer_class = CommunicationCreateSerializer
    permission_classes = [IsAnyLeader]

    def perform_create(self, serializer):
        # Validate audience_filter based on the selected audience type. The audience_filter
        # field is contextual: for "all" or "members_only" audiences it should be empty
        # (the audience is self-explanatory), but for "city" or "category_group" audiences
        # it must contain the specific city name or category to target. This validation
        # prevents leaders from accidentally sending a city-targeted communication without
        # specifying which city.
        audience = serializer.validated_data.get("audience", "all")
        if audience in ("all", "members_only"):
            serializer.validated_data["audience_filter"] = ""
        elif audience in ("city", "category_group"):
            audience_filter = serializer.validated_data.get("audience_filter", "")
            if not audience_filter:
                from rest_framework.exceptions import ValidationError
                raise ValidationError(
                    {"audience_filter": f"audience_filter is required when audience is '{audience}'."}
                )

        instance = serializer.save()
        logger.info(f"Communication created: {instance.reference_number} - {instance.subject}")
        log_action(
            actor=self.request.user,
            action="created",
            model_type="Communication",
            model_id=instance.id,
            new_values={"subject": instance.subject, "reference_number": instance.reference_number},
            request=self.request,
        )
        # Generate image FIRST, then PDF (PDF fallback uses the image)
        logger.info(f"Triggering generation for comm {instance.id}")
        generate_comm_image_task.delay(str(instance.id))
        generate_comm_pdf_task.delay(str(instance.id))
        logger.info(f"Image/PDF tasks dispatched for comm {instance.id}")


class CommunicationDetailView(generics.RetrieveAPIView):
    """GET /kck/comms/{id}/ - authenticated users see all, public sees published."""
    serializer_class = CommunicationDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return Communication.objects.select_related("sender__user").all()
        return Communication.objects.filter(
            status="published", audience="all"
        ).select_related("sender__user")


class CommunicationUpdateView(generics.UpdateAPIView):
    """PUT /kck/comms/{id}/update/"""
    serializer_class = CommunicationCreateSerializer
    permission_classes = [IsAnyLeader]
    queryset = Communication.objects.all()
    lookup_field = "id"

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(f"Communication updated: {instance.reference_number} - {instance.subject}")
        log_action(
            actor=self.request.user,
            action="updated",
            model_type="Communication",
            model_id=instance.id,
            new_values={"subject": instance.subject},
            request=self.request,
        )
        # Re-generate image and PDF after edit
        generate_comm_image_task.delay(str(instance.id))
        generate_comm_pdf_task.delay(str(instance.id))


class CommunicationDeleteView(views.APIView):
    """DELETE /kck/comms/{id}/delete/"""
    permission_classes = [IsAnyLeader]

    def delete(self, request, id):
        try:
            comm = Communication.objects.get(id=id)
        except Communication.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        subject = comm.subject
        comm_id = comm.id
        # Delete associated files
        if comm.pdf_file:
            comm.pdf_file.delete(save=False)
        if comm.image_file:
            comm.image_file.delete(save=False)
        comm.delete()
        log_action(
            actor=request.user,
            action="deleted",
            model_type="Communication",
            model_id=comm_id,
            new_values={"subject": subject},
            request=request,
        )
        return Response({"detail": "Communication deleted."}, status=status.HTTP_204_NO_CONTENT)


class CommunicationStatusView(views.APIView):
    """GET /kck/comms/{id}/status/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            comm = Communication.objects.get(id=id)
        except Communication.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "status": comm.status,
            "has_pdf": bool(comm.pdf_file),
            "has_image": bool(comm.image_file),
        })


class CommunicationPDFView(views.APIView):
    """GET /kck/comms/{id}/pdf/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            comm = Communication.objects.get(id=id)
        except Communication.DoesNotExist:
            raise Http404
        if not comm.pdf_file:
            return Response(
                {"detail": "PDF not yet generated."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return FileResponse(comm.pdf_file.open("rb"), content_type="application/pdf")


class CommunicationImageView(views.APIView):
    """GET /kck/comms/{id}/image/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            comm = Communication.objects.get(id=id)
        except Communication.DoesNotExist:
            raise Http404
        if not comm.image_file:
            return Response(
                {"detail": "Image not yet generated."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return FileResponse(comm.image_file.open("rb"), content_type="image/png")


class CommunicationPublicListView(generics.ListAPIView):
    """GET /kck/comms/public/ - public communications."""
    serializer_class = CommunicationListSerializer
    permission_classes = [AllowAny]
    pagination_class = KCKPagination

    def get_queryset(self):
        return (
            Communication.objects.filter(status="published", audience="all")
            .select_related("sender__user")
        )


class BulkEmailView(views.APIView):
    """
    POST /kck/comms/bulk-email/ - send bulk emails (leaders only).

    The 500-recipient cap is a practical limit to prevent accidental mass-emailing of
    the entire community database in one request. For larger sends, the frontend should
    batch requests. This also keeps individual Celery task payloads manageable and
    reduces the risk of hitting SMTP provider rate limits.
    """
    permission_classes = [IsAnyLeader]

    def post(self, request):
        serializer = BulkEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        from apps.users.models import Membership, User

        recipient_filter = data["recipient_filter"]
        filter_value = data.get("filter_value", "")

        # Support custom recipient list (for sending certs to specific emails)
        custom_emails = request.data.get("recipient_emails")
        if recipient_filter == "custom" and custom_emails:
            emails = [e for e in custom_emails if isinstance(e, str) and "@" in e]
        else:
            qs = User.objects.filter(is_deleted=False, is_active=True)

            if recipient_filter == "members_only":
                active_user_ids = Membership.objects.filter(
                    status="active"
                ).values_list("user_id", flat=True)
                qs = qs.filter(id__in=active_user_ids)
            elif recipient_filter == "by_city":
                if filter_value:
                    qs = qs.filter(city=filter_value)
            elif recipient_filter == "by_category":
                if filter_value:
                    qs = qs.filter(category=filter_value)
            # "all" uses the default qs

            emails = list(qs.exclude(email="").values_list("email", flat=True))

        if not emails:
            return Response(
                {"detail": "No recipients matched the filter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(emails) > 500:
            return Response(
                {"detail": "Cannot send bulk email to more than 500 recipients at once."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        send_bulk_email_task.delay(
            subject=data["subject"],
            body=data["body"],
            recipient_emails=emails,
        )

        return Response({
            "detail": "Bulk email dispatched.",
            "recipient_count": len(emails),
        })


class CommunicationShareImageView(views.APIView):
    """GET /kck/comms/{id}/share-image/ - returns image URL for WhatsApp sharing."""
    permission_classes = [AllowAny]

    def get(self, request, id):
        try:
            comm = Communication.objects.get(id=id)
        except Communication.DoesNotExist:
            raise Http404

        if not comm.image_file:
            return Response(
                {"detail": "Image not yet generated."},
                status=status.HTTP_404_NOT_FOUND,
            )

        image_url = request.build_absolute_uri(comm.image_file.url)
        share_text = f"{comm.subject} - Kenya Community in Korea"
        whatsapp_url = f"https://api.whatsapp.com/send?text={quote(share_text + ' ' + image_url)}"

        return Response({
            "image_url": image_url,
            "share_text": share_text,
            "whatsapp_share_url": whatsapp_url,
        })


# ---------------------------------------------------------------------------
# Announcement views
# ---------------------------------------------------------------------------


class AnnouncementPublicListView(generics.ListAPIView):
    """GET /kck/announcements/ - public list of published announcements."""
    serializer_class = AnnouncementListSerializer
    permission_classes = [AllowAny]
    pagination_class = KCKPagination

    def get_queryset(self):
        qs = Announcement.objects.filter(is_published=True).select_related("author__user")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs


class AnnouncementDetailView(generics.RetrieveAPIView):
    """GET /kck/announcements/{id}/ - public announcement detail."""
    serializer_class = AnnouncementDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        return Announcement.objects.filter(is_published=True).select_related("author__user")


class AnnouncementManageListView(generics.ListAPIView):
    """GET /kck/announcements/manage/ - all announcements for leaders."""
    serializer_class = AnnouncementListSerializer
    permission_classes = [IsAnyLeader]
    pagination_class = KCKPagination

    def get_queryset(self):
        return Announcement.objects.select_related("author__user").all()


class AnnouncementCreateView(generics.CreateAPIView):
    """POST /kck/announcements/create/"""
    serializer_class = AnnouncementCreateSerializer
    permission_classes = [IsAnyLeader]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(
            actor=self.request.user,
            action="created",
            model_type="Announcement",
            model_id=instance.id,
            new_values={"title": instance.title},
            request=self.request,
        )


class AnnouncementUpdateView(generics.UpdateAPIView):
    """PUT /kck/announcements/{id}/update/"""
    serializer_class = AnnouncementCreateSerializer
    permission_classes = [IsAnyLeader]
    queryset = Announcement.objects.all()
    lookup_field = "id"

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(
            actor=self.request.user,
            action="updated",
            model_type="Announcement",
            model_id=instance.id,
            new_values={"title": instance.title},
            request=self.request,
        )


class AnnouncementDeleteView(views.APIView):
    """DELETE /kck/announcements/{id}/delete/"""
    permission_classes = [IsAnyLeader]

    def delete(self, request, id):
        try:
            ann = Announcement.objects.get(id=id)
        except Announcement.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        title = ann.title
        ann_id = ann.id
        if ann.cover_image:
            ann.cover_image.delete(save=False)
        ann.delete()
        log_action(
            actor=request.user,
            action="deleted",
            model_type="Announcement",
            model_id=ann_id,
            new_values={"title": title},
            request=request,
        )
        return Response({"detail": "Announcement deleted."}, status=status.HTTP_204_NO_CONTENT)
