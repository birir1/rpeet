"""
Views for Leader management endpoints.
Author: Meshack Tirop

I organized leader views around the chairman's administrative needs: listing
active leaders (public), creating/updating/deactivating leaders (chairman only),
self-service profile edits (any leader), and granular permission management
(chairman only).
"""
from django.utils import timezone
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.common.audit import log_action
from apps.common.pagination import KCKPagination
from apps.common.permissions import IsAnyLeader, IsChairman

from .models import Leader, LeaderPermission
from .serializers import (
    LeaderCreateSerializer,
    LeaderListSerializer,
    LeaderPermissionSerializer,
    LeaderSelfUpdateSerializer,
    LeaderUpdateSerializer,
)


class LeaderListView(generics.ListAPIView):
    """GET /kck/leaders/ - public, only active leaders."""
    serializer_class = LeaderListSerializer
    permission_classes = [AllowAny]
    pagination_class = KCKPagination

    def get_queryset(self):
        return Leader.objects.filter(is_active=True).select_related("user")


class LeaderCreateView(generics.CreateAPIView):
    """POST /kck/leaders/"""
    serializer_class = LeaderCreateSerializer
    permission_classes = [IsChairman]

    def perform_create(self, serializer):
        chairman_leader = self.request.user.leader
        instance = serializer.save(
            appointed_by=chairman_leader,
            appointed_at=timezone.now(),
        )
        log_action(
            actor=self.request.user,
            action="created",
            model_type="Leader",
            model_id=instance.id,
            new_values=LeaderListSerializer(instance).data,
            request=self.request,
        )


class LeaderUpdateView(generics.UpdateAPIView):
    """PUT /kck/leaders/{id}/"""
    serializer_class = LeaderUpdateSerializer
    permission_classes = [IsChairman]
    queryset = Leader.objects.all()
    lookup_field = "id"

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(
            actor=self.request.user,
            action="updated",
            model_type="Leader",
            model_id=instance.id,
            new_values=LeaderListSerializer(instance).data,
            request=self.request,
        )


class LeaderSelfUpdateView(generics.UpdateAPIView):
    """PUT /kck/leaders/me/ - leaders update their own profile."""
    serializer_class = LeaderSelfUpdateSerializer
    permission_classes = [IsAnyLeader]

    def get_object(self):
        return self.request.user.leader


class LeaderDeactivateView(views.APIView):
    """POST /kck/leaders/{id}/deactivate/"""
    permission_classes = [IsChairman]

    def post(self, request, id):
        try:
            leader = Leader.objects.get(id=id)
        except Leader.DoesNotExist:
            return Response(
                {"detail": "Leader not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        leader.is_active = False
        leader.save(update_fields=["is_active", "updated_at"])
        log_action(
            actor=request.user,
            action="updated",
            model_type="Leader",
            model_id=leader.id,
            new_values={"is_active": False},
            request=request,
        )
        return Response(LeaderListSerializer(leader).data)


class LeaderPermissionView(views.APIView):
    """GET/PUT /kck/leaders/{id}/permissions/ - chairman only."""
    permission_classes = [IsChairman]

    def get(self, request, id):
        # I intentionally do NOT auto-create a LeaderPermission row on GET.
        # Earlier versions used get_or_create here, but that caused a side
        # effect: simply viewing permissions would create a row with defaults,
        # making it impossible to distinguish "never configured" from
        # "explicitly set to defaults". Now GET returns 404 if permissions
        # haven't been set, which is the honest answer.
        try:
            leader = Leader.objects.get(id=id)
        except Leader.DoesNotExist:
            return Response({"detail": "Leader not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            perms = leader.permissions
        except LeaderPermission.DoesNotExist:
            return Response(
                {"detail": "Permissions not found for this leader."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LeaderPermissionSerializer(perms)
        return Response(serializer.data)

    def put(self, request, id):
        try:
            leader = Leader.objects.get(id=id)
        except Leader.DoesNotExist:
            return Response({"detail": "Leader not found."}, status=status.HTTP_404_NOT_FOUND)

        # I use get_or_create only in PUT so that the first permission update
        # for a leader seeds the row with role-appropriate defaults (e.g.,
        # treasurer gets can_view_financials=True). Subsequent PUTs then
        # update the existing row. This keeps the write path simple while
        # avoiding the GET side-effect issue described above.
        from .models import ROLE_DEFAULT_PERMISSIONS
        defaults = ROLE_DEFAULT_PERMISSIONS.get(leader.role, {})
        perms, _created = LeaderPermission.objects.get_or_create(
            leader=leader, defaults=defaults,
        )

        serializer = LeaderPermissionSerializer(perms, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        log_action(
            actor=request.user,
            action="updated",
            model_type="LeaderPermission",
            model_id=perms.id,
            new_values=serializer.data,
            request=request,
        )
        return Response(serializer.data)
