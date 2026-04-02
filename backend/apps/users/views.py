"""
Views for User, Membership, and Auth endpoints.

This module handles all user-facing API endpoints: registration, login, password reset,
user CRUD, membership lifecycle, and reporting. I organized views into three sections:
Auth (public-facing), User (secretary-managed), and Membership (treasurer-managed).

Rate limiting is applied per-IP to protect against brute-force attacks on auth endpoints.
We use django-ratelimit decorators rather than DRF throttling because ratelimit gives us
more granular control (per-view, per-method) and integrates cleanly with Django's cache
framework.

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
import csv

from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.common.audit import log_action
from apps.common.pagination import KCKPagination
from apps.common.permissions import IsChairman, IsOwnerOrSecretary, IsSecretary, IsTreasurer

from .models import Membership, User
from .serializers import (
    MeSerializer,
    MembershipRequestSerializer,
    MembershipSerializer,
    MembershipUpdateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
)


# ===================================================================
# Auth views
# ===================================================================
class RegisterView(generics.CreateAPIView):
    """POST /kck/auth/register/"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    # Rate limit: 3 registrations per minute per IP. Registration is expensive (sends
    # verification email, creates DB records) so we keep this tight to prevent spam
    # account creation. Legitimate users never register more than once.
    @method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=True))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate email verification token and send verification email
        import secrets
        token = secrets.token_urlsafe(32)
        user.email_verification_token = token
        user.save(update_fields=["email_verification_token"])

        from django.core.mail import send_mail
        verify_url = f"{request.META.get('HTTP_ORIGIN', 'http://localhost:8080')}/verify-email/{token}"
        send_mail(
            subject="Verify your KCK account",
            message=f"Click this link to verify your email: {verify_url}",
            from_email=None,
            recipient_list=[user.email],
            fail_silently=True,
        )

        log_action(
            actor=user,
            action="created",
            model_type="User",
            model_id=user.id,
            new_values={"email": user.email, "full_name": user.full_name},
            request=request,
        )
        return Response(
            UserListSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """POST /kck/auth/login/ - returns tokens + user data."""
    permission_classes = [AllowAny]

    # Rate limit: 5 login attempts per minute per IP. This is more generous than
    # registration because users may mistype passwords. 5/min strikes a balance between
    # usability (allows a few retries) and security (limits brute-force attacks).
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response(
                {"detail": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user exists and is not soft-deleted before attempting auth
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return Response(
                {"detail": "No active account found with the given credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.is_deleted:
            return Response(
                {"detail": "No active account found with the given credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            leader = getattr(user, 'leader', None)
            role = leader.role if leader and leader.is_active else 'member'
            response.data['user'] = {
                'id': str(user.id),
                'full_name': user.full_name,
                'email': user.email,
                'role': role,
                'is_verified': user.is_verified,
                'city': user.city,
                'category': user.category,
            }
        return response


@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='post')
class TokenRefreshView_(TokenRefreshView):
    """POST /kck/auth/token/refresh/"""
    permission_classes = [AllowAny]


class LogoutView(views.APIView):
    """POST /kck/auth/logout/ - blacklist refresh token."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Logged out."}, status=status.HTTP_200_OK)


class MeView(views.APIView):
    """GET /kck/auth/me/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)


class PasswordResetRequestView(views.APIView):
    """
    POST /kck/auth/password-reset/ -- send reset token via email.

    I use Django's cache framework (Redis in production, locmem in dev) to store
    password reset tokens instead of a database model. This avoids adding a table
    for short-lived tokens and gives us automatic expiry via cache TTL. The 1-hour
    timeout is standard for password reset flows.

    Security note: we always return the same response message regardless of whether
    the email exists in our system. This prevents user enumeration attacks where an
    attacker could probe our API to discover which email addresses are registered.
    """
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='3/h', method='POST', block=True))
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, is_deleted=False)
        except User.DoesNotExist:
            return Response({"detail": "If this email is registered, a reset link has been sent."})

        import secrets
        token = secrets.token_urlsafe(32)

        from django.core.cache import cache
        cache.set(f"password_reset_{token}", str(user.id), timeout=3600)

        # Send email (console in dev)
        from django.core.mail import send_mail
        reset_url = f"{request.META.get('HTTP_ORIGIN', 'http://localhost:8080')}/password-reset/{token}"
        send_mail(
            subject="KCK Password Reset",
            message=f"Click this link to reset your password: {reset_url}\n\nThis link expires in 1 hour.",
            from_email=None,
            recipient_list=[email],
            fail_silently=True,
        )

        return Response({"detail": "If this email is registered, a reset link has been sent."})


class PasswordResetConfirmView(views.APIView):
    """POST /kck/auth/password-reset/confirm/ — set new password with token."""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token', '')
        new_password = request.data.get('new_password', '')

        if not token or not new_password:
            return Response({"detail": "Token and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response({"detail": "Password must be at least 8 characters."}, status=status.HTTP_400_BAD_REQUEST)

        from django.core.cache import cache
        user_id = cache.get(f"password_reset_{token}")
        if not user_id:
            return Response({"detail": "Invalid or expired reset token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save(update_fields=["password"])

        # Invalidate token
        cache.delete(f"password_reset_{token}")

        return Response({"detail": "Password has been reset successfully. You can now log in."})


class EmailVerifyView(views.APIView):
    """GET /kck/auth/verify-email/{token}/ — verify email address."""
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            user = User.objects.get(email_verification_token=token, is_deleted=False)
        except User.DoesNotExist:
            return Response({"detail": "Invalid verification token."}, status=status.HTTP_400_BAD_REQUEST)

        user.email_verified = True
        user.email_verification_token = ""
        user.save(update_fields=["email_verified", "email_verification_token"])

        return Response({"detail": "Email verified successfully. You can now log in."})


# ===================================================================
# User views
# ===================================================================
class UserListView(generics.ListAPIView):
    """GET /kck/users/"""
    serializer_class = UserListSerializer
    permission_classes = [IsSecretary]
    pagination_class = KCKPagination

    def get_queryset(self):
        qs = User.objects.filter(is_deleted=False)
        city = self.request.query_params.get("city")
        category = self.request.query_params.get("category")
        verified = self.request.query_params.get("verified")
        search = self.request.query_params.get("search")
        if city:
            qs = qs.filter(city=city)
        if category:
            qs = qs.filter(category=category)
        if verified is not None:
            qs = qs.filter(is_verified=verified.lower() == "true")
        if search:
            qs = qs.filter(full_name__icontains=search)
        return qs


class UserDetailView(generics.RetrieveAPIView):
    """GET /kck/users/{id}/"""
    serializer_class = UserDetailSerializer
    permission_classes = [IsOwnerOrSecretary]
    queryset = User.objects.filter(is_deleted=False)
    lookup_field = "id"


class UserUpdateView(generics.UpdateAPIView):
    """PUT /kck/users/{id}/"""
    serializer_class = UserUpdateSerializer
    permission_classes = [IsOwnerOrSecretary]
    queryset = User.objects.filter(is_deleted=False)
    lookup_field = "id"

    def perform_update(self, serializer):
        old = self.get_object()
        old_data = UserDetailSerializer(old, context=self.get_serializer_context()).data
        instance = serializer.save()
        new_data = UserDetailSerializer(instance, context=self.get_serializer_context()).data
        log_action(
            actor=self.request.user,
            action="updated",
            model_type="User",
            model_id=instance.id,
            old_values=old_data,
            new_values=new_data,
            request=self.request,
        )


class UserVerifyView(views.APIView):
    """POST /kck/users/{id}/verify/"""
    permission_classes = [IsSecretary]

    def post(self, request, id):
        try:
            user = User.objects.get(id=id, is_deleted=False)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.is_verified = True
        user.verified_by = request.user.leader
        user.verified_at = timezone.now()
        user.save(update_fields=["is_verified", "verified_by", "verified_at", "updated_at"])
        log_action(
            actor=request.user,
            action="verified",
            model_type="User",
            model_id=user.id,
            new_values={"is_verified": True},
            request=request,
        )
        return Response(UserDetailSerializer(user, context={"request": request}).data)


class BulkVerifyView(views.APIView):
    """
    POST /kck/users/bulk-verify/

    I use Django's bulk_update() instead of saving each user in a loop because
    verification is a simple field update that doesn't trigger signals or complex
    save logic. bulk_update issues a single SQL UPDATE statement, which is dramatically
    faster when the secretary is verifying 50-100 newly registered members after an event.
    The 100-user cap prevents accidental mass-verification of the entire database.
    """
    permission_classes = [IsSecretary]

    def post(self, request):
        user_ids = request.data.get("user_ids", [])
        if not user_ids or not isinstance(user_ids, list):
            return Response(
                {"detail": "user_ids must be a non-empty list of UUIDs."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(user_ids) > 100:
            return Response(
                {"detail": "Cannot bulk-verify more than 100 users at once."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        leader = request.user.leader
        now = timezone.now()

        with transaction.atomic():
            users = list(
                User.objects.filter(id__in=user_ids, is_deleted=False, is_verified=False)
            )
            for user in users:
                user.is_verified = True
                user.verified_by = leader
                user.verified_at = now

            User.objects.bulk_update(users, ["is_verified", "verified_by", "verified_at"])

            # Audit log per user (keeps format consistent with single-verify)
            for user in users:
                log_action(
                    actor=request.user,
                    action="verified",
                    model_type="User",
                    model_id=user.id,
                    new_values={"is_verified": True, "bulk": True, "user_id": str(user.id)},
                    request=request,
                )

        return Response({"verified_count": len(users)}, status=status.HTTP_200_OK)


class UserDeleteView(views.APIView):
    """DELETE /kck/users/{id}/ - soft delete"""
    permission_classes = [IsChairman]

    def delete(self, request, id):
        try:
            user = User.objects.get(id=id, is_deleted=False)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.soft_delete()
        log_action(
            actor=request.user,
            action="deleted",
            model_type="User",
            model_id=user.id,
            request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserExportView(views.APIView):
    """GET /kck/users/export/ - CSV download"""
    permission_classes = [IsSecretary]

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="kck_users.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "Full Name", "Email", "Phone", "City", "Category",
            "Visa Type", "Verified", "Created",
        ])
        users = User.objects.filter(is_deleted=False).order_by("full_name")
        for u in users:
            writer.writerow([
                u.full_name, u.email, u.phone, u.city, u.category,
                u.visa_type, u.is_verified, u.created_at.isoformat(),
            ])
        return response


class UserMapDataView(views.APIView):
    """GET /kck/users/map-data/ - city distribution for map"""
    permission_classes = [IsSecretary]

    def get(self, request):
        from django.db.models import Count
        data = (
            User.objects.filter(is_deleted=False)
            .values("city")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        return Response(list(data))


# ===================================================================
# Membership views
# ===================================================================
class MembershipListCreateView(generics.ListCreateAPIView):
    """GET/POST /kck/memberships/"""
    serializer_class = MembershipSerializer
    permission_classes = [IsTreasurer]
    pagination_class = KCKPagination

    def get_queryset(self):
        qs = Membership.objects.select_related("user", "recorded_by").all()
        user_id = self.request.query_params.get("user")
        stat = self.request.query_params.get("status")
        payment_stat = self.request.query_params.get("payment_status")
        if user_id:
            qs = qs.filter(user_id=user_id)
        if stat:
            qs = qs.filter(status=stat)
        if payment_stat:
            qs = qs.filter(payment_status=payment_stat)
        return qs

    def perform_create(self, serializer):
        instance = serializer.save()
        # The json.loads(json.dumps(..., default=str)) round-trip is a UUID serialization
        # fix. DRF serializers return UUID objects in .data, but AuditLog stores JSON.
        # The default=str ensures UUIDs, dates, and Decimals are converted to strings
        # before being saved to the JSONField.
        import json
        log_data = json.loads(json.dumps(MembershipSerializer(instance).data, default=str))
        log_action(
            actor=self.request.user,
            action="created",
            model_type="Membership",
            model_id=instance.id,
            new_values=log_data,
            request=self.request,
        )


class MembershipDetailView(generics.RetrieveUpdateAPIView):
    """GET/PUT /kck/memberships/{id}/"""
    permission_classes = [IsTreasurer]
    queryset = Membership.objects.select_related("user", "recorded_by").all()
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return MembershipUpdateSerializer
        return MembershipSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        import json
        log_data = json.loads(json.dumps(MembershipSerializer(instance).data, default=str))
        log_action(
            actor=self.request.user,
            action="updated",
            model_type="Membership",
            model_id=instance.id,
            new_values=log_data,
            request=self.request,
        )


class MembershipRenewView(views.APIView):
    """
    POST /kck/memberships/{id}/renew/ - extend membership by 1 year.

    Renewal is done in-place on the existing Membership record rather than creating a
    new one. I chose this approach because a membership represents a continuous
    relationship with the community, not a discrete purchase. Creating new records
    would fragment the member's payment history and make reporting harder for the
    treasurer. The renewal_history JSON field on the Membership model preserves the
    full chain of extensions.
    """
    permission_classes = [IsTreasurer]

    def post(self, request, id):
        try:
            membership = Membership.objects.select_related("user").get(id=id)
        except Membership.DoesNotExist:
            return Response({"detail": "Membership not found."}, status=status.HTTP_404_NOT_FOUND)

        old_expiry = str(membership.expiry_date)
        membership.renew(renewed_by=request.user.full_name)

        log_action(
            actor=request.user,
            action="updated",
            model_type="Membership",
            model_id=membership.id,
            new_values={
                "action": "renewed",
                "old_expiry": old_expiry,
                "new_expiry": str(membership.expiry_date),
                "renewal_count": membership.renewal_count,
            },
            request=request,
        )

        return Response({
            "id": str(membership.id),
            "user_name": membership.user.full_name,
            "status": membership.status,
            "expiry_date": str(membership.expiry_date),
            "renewal_count": membership.renewal_count,
            "message": f"Membership renewed for {membership.user.full_name}. New expiry: {membership.expiry_date}",
        })


class MembershipMineView(views.APIView):
    """
    GET /kck/memberships/mine/ - current user's memberships.

    Returns both a "current" membership (the first active or pending one found) and
    the full history. The "current" detection logic iterates through memberships ordered
    by start_date descending and picks the first active/pending one. This handles the
    edge case where a user might have an old expired membership and a new pending one --
    we always surface the most relevant one to the frontend.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = Membership.objects.filter(
            user=request.user
        ).order_by("-start_date")
        data = MembershipSerializer(memberships, many=True).data
        current = None
        for m in data:
            if m.get("status") in ("active", "pending"):
                current = m
                break
        return Response({
            "current": current,
            "history": data,
        })


class MembershipRequestView(views.APIView):
    """POST /kck/memberships/request/ - authenticated user requests membership."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MembershipRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        from datetime import date
        from apps.analytics.models import SiteSetting

        try:
            fee_setting = SiteSetting.objects.get(key='membership_fee')
            fee_amount = fee_setting.value.get('amount', 50000)
            treasurer_email = fee_setting.value.get('treasurer_email', 'finance@kenyakorea.com')
        except SiteSetting.DoesNotExist:
            fee_amount = 50000
            treasurer_email = "finance@kenyakorea.com"

        # Check if user already has an active or pending membership
        existing = Membership.objects.filter(user=request.user).order_by("-expiry_date").first()

        if existing and existing.status == "active":
            return Response(
                {"detail": "You already have an active membership.", "expiry_date": str(existing.expiry_date)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if existing and existing.status == "pending":
            return Response(
                {"detail": "You already have a pending membership request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create membership (first time or after expiry)
        membership = Membership.objects.create(
            user=request.user,
            status="pending",
            start_date=date.today(),
            fee_amount=fee_amount,
            currency="KRW",
            payment_method=data.get("payment_method", ""),
            payment_reference=data.get("payment_reference", ""),
            notes=data.get("notes", ""),
            payment_status="pending_verification",
        )
        if "payment_screenshot" in data:
            membership.payment_screenshot = data["payment_screenshot"]
            membership.save(update_fields=["payment_screenshot"])

        return Response(
            {
                "membership_id": str(membership.id),
                "status": membership.status,
                "payment_status": membership.payment_status,
                "treasurer_email": treasurer_email,
                "message": "Membership request submitted. Please send payment and await verification.",
            },
            status=status.HTTP_201_CREATED,
        )


class MembershipReportView(views.APIView):
    """GET /kck/memberships/report/ - summary statistics"""
    permission_classes = [IsTreasurer]

    def get(self, request):
        from django.db.models import Count, Sum
        total = Membership.objects.count()
        active = Membership.objects.filter(status="active").count()
        expired = Membership.objects.filter(status="expired").count()
        revenue = Membership.objects.filter(status="active").aggregate(
            total=Sum("fee_amount")
        )["total"] or 0
        return Response({
            "total": total,
            "active": active,
            "expired": expired,
            "pending": Membership.objects.filter(status="pending").count(),
            "cancelled": Membership.objects.filter(status="cancelled").count(),
            "total_revenue": str(revenue),
        })
