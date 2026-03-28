"""
Views for Event endpoints.

Events support a draft/published workflow. By default, the public list only shows
published events. Committee members and the chairman can access draft events via the
?manage=true query parameter for editing before publication.

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
from django.utils import timezone
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.common.audit import log_action
from apps.common.pagination import KCKPagination
from apps.common.permissions import IsCommittee

from .models import Event, EventAttendee, EventPhoto
from .serializers import (
    BatchAttendeeInputSerializer,
    EventAttendeeListSerializer,
    EventCreateUpdateSerializer,
    EventDetailSerializer,
    EventListSerializer,
    EventPhotoUploadSerializer,
)


class EventListView(generics.ListAPIView):
    """GET /kck/events/ - public, only published."""
    serializer_class = EventListSerializer
    permission_classes = [AllowAny]
    pagination_class = KCKPagination

    def get_queryset(self):
        # The ?manage=true parameter lets the frontend toggle between "public view"
        # (published events only) and "management view" (all events including drafts).
        # We verify the requesting user is actually a leader before showing drafts --
        # a regular user passing ?manage=true still only sees published events.
        manage = self.request.query_params.get("manage") == "true"
        if manage and self.request.user.is_authenticated:
            from apps.leaders.models import Leader
            is_leader = Leader.objects.filter(user=self.request.user, is_active=True).exists()
            if is_leader:
                qs = Event.objects.select_related("created_by__user").all()
            else:
                qs = Event.objects.filter(is_published=True).select_related("created_by__user")
        else:
            qs = Event.objects.filter(is_published=True).select_related("created_by__user")

        event_type = self.request.query_params.get("type")
        if event_type == "past":
            qs = qs.filter(event_date__lt=timezone.now().date())
        elif event_type == "upcoming":
            qs = qs.filter(event_date__gte=timezone.now().date())
        return qs


class EventDetailView(generics.RetrieveAPIView):
    """GET /kck/events/{slug}/ - public."""
    serializer_class = EventDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return (
            Event.objects.filter(is_published=True)
            .select_related("created_by__user")
            .prefetch_related("photos")
        )


class EventCreateView(generics.CreateAPIView):
    """POST /kck/events/"""
    serializer_class = EventCreateUpdateSerializer
    permission_classes = [IsCommittee]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(
            actor=self.request.user,
            action="created",
            model_type="Event",
            model_id=instance.id,
            new_values={"title": instance.title},
            request=self.request,
        )


class EventDetailByIdView(generics.RetrieveAPIView):
    """GET /kck/events/{id}/detail/ - for committee editing (includes unpublished)."""
    serializer_class = EventDetailSerializer
    permission_classes = [IsCommittee]
    queryset = Event.objects.all().select_related("created_by__user").prefetch_related("photos")
    lookup_field = "id"


class EventUpdateView(generics.UpdateAPIView):
    """PUT /kck/events/{id}/"""
    serializer_class = EventCreateUpdateSerializer
    permission_classes = [IsCommittee]
    queryset = Event.objects.all()
    lookup_field = "id"

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(
            actor=self.request.user,
            action="updated",
            model_type="Event",
            model_id=instance.id,
            new_values={"title": instance.title},
            request=self.request,
        )


class EventPhotoUploadView(views.APIView):
    """POST /kck/events/{id}/photos/"""
    permission_classes = [IsCommittee]

    def post(self, request, id):
        try:
            event = Event.objects.get(id=id)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EventPhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        photo = serializer.save(event=event, uploaded_by=request.user.leader)
        return Response(
            EventPhotoUploadSerializer(photo).data,
            status=status.HTTP_201_CREATED,
        )


class EventPublishView(views.APIView):
    """
    POST /kck/events/{id}/publish/

    Separate publish endpoint rather than a status field on the update serializer.
    I chose this design because publishing is a deliberate action that should be
    audited distinctly from regular edits. The audit log records a "published" action
    type, making it easy to see when and by whom each event was made public.
    """
    permission_classes = [IsCommittee]

    def post(self, request, id):
        try:
            event = Event.objects.get(id=id)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

        event.is_published = True
        event.save(update_fields=["is_published", "updated_at"])
        log_action(
            actor=request.user,
            action="published",
            model_type="Event",
            model_id=event.id,
            new_values={"is_published": True},
            request=request,
        )
        return Response(EventDetailSerializer(event).data)


class EventAttendeeView(views.APIView):
    """GET/POST /kck/events/{id}/attendees/"""
    permission_classes = [IsCommittee]

    def get(self, request, id):
        """List all attendees for an event."""
        try:
            event = Event.objects.get(id=id)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

        attendees = EventAttendee.objects.filter(event=event)
        serializer = EventAttendeeListSerializer(attendees, many=True)
        return Response(serializer.data)

    def post(self, request, id):
        """Bulk create attendees."""
        try:
            event = Event.objects.get(id=id)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BatchAttendeeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attendees_data = serializer.validated_data["attendees"]
        created = []
        for item in attendees_data:
            attendee = EventAttendee.objects.create(
                event=event,
                name=item["name"],
                email=item.get("email", ""),
                user_id=item.get("user_id") or None,
                attended=item.get("attended", True),
            )
            created.append(attendee)

        return Response(
            {
                "success": True,
                "data": {
                    "attendees_created": len(created),
                    "attendees": EventAttendeeListSerializer(created, many=True).data,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class EventDeleteView(views.APIView):
    """DELETE /kck/events/{id}/delete/"""
    permission_classes = [IsCommittee]

    def delete(self, request, id):
        try:
            event = Event.objects.get(id=id)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

        title = event.title
        event_id = event.id
        # Deleting the event cascades to photos and attendees (on_delete=CASCADE)
        event.delete()
        log_action(
            actor=request.user,
            action="deleted",
            model_type="Event",
            model_id=event_id,
            new_values={"title": title},
            request=request,
        )
        return Response({"detail": "Event deleted."}, status=status.HTTP_204_NO_CONTENT)


class EventPhotoDeleteView(views.APIView):
    """DELETE /kck/events/{event_id}/photos/{photo_id}/"""
    permission_classes = [IsCommittee]

    def delete(self, request, event_id, photo_id):
        try:
            photo = EventPhoto.objects.get(id=photo_id, event_id=event_id)
        except EventPhoto.DoesNotExist:
            return Response({"detail": "Photo not found."}, status=status.HTTP_404_NOT_FOUND)

        photo.delete()
        log_action(
            actor=request.user,
            action="deleted",
            model_type="EventPhoto",
            model_id=photo_id,
            new_values={"event_id": str(event_id)},
            request=request,
        )
        return Response({"detail": "Photo deleted."}, status=status.HTTP_204_NO_CONTENT)


class EventBatchCertsView(views.APIView):
    """POST /kck/events/{id}/batch-certs/ - generate certs for all attendees."""
    permission_classes = [IsCommittee]

    def post(self, request, id):
        from apps.certificates.models import Certificate
        from apps.certificates.tasks import (
            generate_cert_image_task,
            generate_cert_pdf_task,
            generate_qr_task,
            send_cert_email_task,
        )

        try:
            event = Event.objects.get(id=id)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

        attendees = EventAttendee.objects.filter(event=event, attended=True)
        if not attendees.exists():
            return Response(
                {"detail": "No attendees found for this event."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        leader = request.user.leader
        certs_created = 0
        emails_queued = 0

        for attendee in attendees:
            cert = Certificate.objects.create(
                cert_type="participation",
                event=event,
                recipient_name=attendee.name,
                recipient_user=attendee.user,
                body=(
                    f"This certificate is awarded to {attendee.name} "
                    f"for participating in {event.title} "
                    f"held on {event.event_date.strftime('%d %B %Y')} "
                    f"at {event.location or 'Kenya Community in Korea'}."
                ),
                issued_by=leader,
            )
            generate_cert_image_task.delay(str(cert.id))
            generate_qr_task.delay(str(cert.id))
            generate_cert_pdf_task.delay(str(cert.id))
            certs_created += 1

            # Queue email if attendee has an email (either from attendee record or user)
            has_email = bool(attendee.email) or (attendee.user and attendee.user.email)
            if has_email:
                send_cert_email_task.delay(str(cert.id))
                emails_queued += 1

        return Response({
            "success": True,
            "data": {
                "certificates_created": certs_created,
                "emails_queued": emails_queued,
            },
        })
