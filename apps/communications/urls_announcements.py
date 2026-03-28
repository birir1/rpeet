"""
Announcement URL configuration.
Prefix: /kck/announcements/
"""
from django.urls import path

from .views import (
    AnnouncementCreateView,
    AnnouncementDeleteView,
    AnnouncementDetailView,
    AnnouncementManageListView,
    AnnouncementPublicListView,
    AnnouncementUpdateView,
)

urlpatterns = [
    path("", AnnouncementPublicListView.as_view(), name="announcement-list"),
    path("manage/", AnnouncementManageListView.as_view(), name="announcement-manage"),
    path("create/", AnnouncementCreateView.as_view(), name="announcement-create"),
    path("<uuid:id>/", AnnouncementDetailView.as_view(), name="announcement-detail"),
    path("<uuid:id>/update/", AnnouncementUpdateView.as_view(), name="announcement-update"),
    path("<uuid:id>/delete/", AnnouncementDeleteView.as_view(), name="announcement-delete"),
]
