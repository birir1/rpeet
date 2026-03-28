"""
Leader URL configuration.
Prefix: /kck/leaders/
"""
from django.urls import path

from .views import (
    LeaderCreateView,
    LeaderDeactivateView,
    LeaderListView,
    LeaderPermissionView,
    LeaderSelfUpdateView,
    LeaderUpdateView,
)

urlpatterns = [
    path("", LeaderListView.as_view(), name="leader-list"),
    path("create/", LeaderCreateView.as_view(), name="leader-create"),
    path("me/", LeaderSelfUpdateView.as_view(), name="leader-self-update"),
    path("<uuid:id>/", LeaderUpdateView.as_view(), name="leader-update"),
    path("<uuid:id>/deactivate/", LeaderDeactivateView.as_view(), name="leader-deactivate"),
    path("<uuid:id>/permissions/", LeaderPermissionView.as_view(), name="leader-permissions"),
]
