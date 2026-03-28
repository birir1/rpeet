"""
Event URL configuration.
Prefix: /kck/events/
"""
from django.urls import path

from .views import (
    EventAttendeeView,
    EventBatchCertsView,
    EventCreateView,
    EventDeleteView,
    EventDetailByIdView,
    EventDetailView,
    EventListView,
    EventPhotoDeleteView,
    EventPhotoUploadView,
    EventPublishView,
    EventUpdateView,
)

urlpatterns = [
    path("", EventListView.as_view(), name="event-list"),
    path("create/", EventCreateView.as_view(), name="event-create"),
    path("<uuid:id>/detail/", EventDetailByIdView.as_view(), name="event-detail-by-id"),
    path("<uuid:id>/update/", EventUpdateView.as_view(), name="event-update"),
    path("<uuid:id>/delete/", EventDeleteView.as_view(), name="event-delete"),
    path("<uuid:id>/photos/", EventPhotoUploadView.as_view(), name="event-photos"),
    path("<uuid:event_id>/photos/<uuid:photo_id>/", EventPhotoDeleteView.as_view(), name="event-photo-delete"),
    path("<uuid:id>/publish/", EventPublishView.as_view(), name="event-publish"),
    path("<uuid:id>/attendees/", EventAttendeeView.as_view(), name="event-attendees"),
    path("<uuid:id>/batch-certs/", EventBatchCertsView.as_view(), name="event-batch-certs"),
    path("<slug:slug>/", EventDetailView.as_view(), name="event-detail"),
]
