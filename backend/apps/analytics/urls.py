"""
Analytics URL configuration.
Prefix: /kck/analytics/
"""
from django.urls import path

from .views import (
    CategoriesView,
    CitiesView,
    MembershipAnalyticsView,
    MembershipFeeView,
    OverviewView,
)

urlpatterns = [
    path("overview/", OverviewView.as_view(), name="analytics-overview"),
    path("cities/", CitiesView.as_view(), name="analytics-cities"),
    path("categories/", CategoriesView.as_view(), name="analytics-categories"),
    path("membership/", MembershipAnalyticsView.as_view(), name="analytics-membership"),
]

# Settings URL patterns (will be included separately at /kck/settings/)
settings_urlpatterns = [
    path("membership-fee/", MembershipFeeView.as_view(), name="settings-membership-fee"),
]
