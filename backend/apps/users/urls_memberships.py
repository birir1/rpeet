"""
Membership URL configuration for the KCK platform.
Author: Meshack Tirop

Routes for membership CRUD, self-service requests, renewals, and reporting.
All endpoints are prefixed with /kck/memberships/.
"""
from django.urls import path

from .views import (
    MembershipDetailView,
    MembershipListCreateView,
    MembershipMineView,
    MembershipRenewView,
    MembershipReportView,
    MembershipRequestView,
)

urlpatterns = [
    path("", MembershipListCreateView.as_view(), name="membership-list"),
    path("mine/", MembershipMineView.as_view(), name="membership-mine"),
    path("request/", MembershipRequestView.as_view(), name="membership-request"),
    path("report/", MembershipReportView.as_view(), name="membership-report"),
    path("<uuid:id>/", MembershipDetailView.as_view(), name="membership-detail"),
    path("<uuid:id>/renew/", MembershipRenewView.as_view(), name="membership-renew"),
]
