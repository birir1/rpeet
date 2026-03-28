"""
Analytics and site settings views for the KCK dashboard.
Author: Meshack Tirop

I split analytics into role-gated views: OverviewView serves both public
visitors (basic member counts for the landing page) and the chairman (full
operational metrics including revenue and unverified user counts). The other
views are restricted to specific leadership roles -- the secretary sees
demographic breakdowns, the treasurer sees financial data.
"""
from django.db.models import Count, Sum
from rest_framework import views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.common.permissions import IsChairman, IsSecretary, IsTreasurer
from apps.users.models import Membership, User
from .models import SiteSetting


class OverviewView(views.APIView):
    """
    GET /kck/analytics/overview/
    Chairman gets full data; unauthenticated gets limited public stats.

    I use AllowAny here because the frontend landing page needs basic member
    counts without requiring login. The chairman check happens inside the
    handler rather than at the permission level so that public users still get
    the limited dataset. If I used IsChairman as the permission class, public
    visitors would get a 403 instead of the partial data they need.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        total_users = User.objects.filter(is_deleted=False).count()
        verified_users = User.objects.filter(is_deleted=False, is_verified=True).count()

        # Public data
        data = {
            "total_members": total_users,
            "verified_members": verified_users,
        }

        # Check if user is chairman for extended stats
        is_chair = False
        if request.user and request.user.is_authenticated:
            try:
                leader = request.user.leader
                if leader.is_active and leader.role == "chairman":
                    is_chair = True
            except Exception:
                pass

        if is_chair:
            active_memberships = Membership.objects.filter(status="active").count()
            total_revenue = Membership.objects.filter(status="active").aggregate(
                total=Sum("fee_amount")
            )["total"] or 0

            from apps.events.models import Event
            from apps.communications.models import Communication

            data.update({
                "active_memberships": active_memberships,
                "total_revenue": str(total_revenue),
                "total_events": Event.objects.count(),
                "published_events": Event.objects.filter(is_published=True).count(),
                "total_communications": Communication.objects.count(),
                "unverified_users": User.objects.filter(is_deleted=False, is_verified=False).count(),
            })

        return Response(data)


class CitiesView(views.APIView):
    """GET /kck/analytics/cities/"""
    permission_classes = [IsSecretary]

    def get(self, request):
        data = (
            User.objects.filter(is_deleted=False)
            .values("city")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        return Response(list(data))


class CategoriesView(views.APIView):
    """GET /kck/analytics/categories/"""
    permission_classes = [IsSecretary]

    CATEGORY_COLORS = {
        "student": "#003366",
        "worker": "#CC0000",
        "professional": "#F4A460",
        "tourist": "#2E8B57",
    }

    def get(self, request):
        qs = (
            User.objects.filter(is_deleted=False)
            .values("category")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        data = []
        for item in qs:
            data.append({
                "category": item["category"],
                "count": item["count"],
                "color": self.CATEGORY_COLORS.get(item["category"], "#888888"),
            })
        return Response({"data": data})


class MembershipAnalyticsView(views.APIView):
    """GET /kck/analytics/membership/"""
    permission_classes = [IsTreasurer]

    def get(self, request):
        by_status = (
            Membership.objects.values("status")
            .annotate(count=Count("id"), total=Sum("fee_amount"))
            .order_by("status")
        )
        result = []
        for item in by_status:
            result.append({
                "status": item["status"],
                "count": item["count"],
                "total_amount": str(item["total"] or 0),
            })
        return Response(result)


class MembershipFeeView(views.APIView):
    """
    GET /kck/settings/membership-fee/ - public, returns current fee.
    PUT /kck/settings/membership-fee/ - chairman only, updates fee.
    """

    def get_permissions(self):
        if self.request.method == "PUT":
            return [IsChairman()]
        return [AllowAny()]

    def get(self, request):
        setting = SiteSetting.objects.filter(key="membership_fee").first()
        if setting:
            return Response(setting.value)
        return Response({
            "amount": 50000,
            "currency": "KRW",
            "treasurer_email": "treasurer@kck.or.ke",
        })

    def put(self, request):
        amount = request.data.get("amount", 50000)
        currency = request.data.get("currency", "KRW")
        treasurer_email = request.data.get("treasurer_email", "treasurer@kck.or.ke")

        value = {
            "amount": amount,
            "currency": currency,
            "treasurer_email": treasurer_email,
        }

        setting, _ = SiteSetting.objects.update_or_create(
            key="membership_fee",
            defaults={"value": value},
        )
        return Response(setting.value)
