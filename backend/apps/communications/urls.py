"""
Communication URL configuration.
Prefix: /kck/comms/
"""
from django.urls import path

from .views import (
    BulkEmailView,
    CommunicationCreateView,
    CommunicationDeleteView,
    CommunicationDetailView,
    CommunicationImageView,
    CommunicationListView,
    CommunicationPDFView,
    CommunicationPublicListView,
    CommunicationShareImageView,
    CommunicationStatusView,
    CommunicationUpdateView,
)

urlpatterns = [
    path("", CommunicationListView.as_view(), name="comm-list"),
    path("create/", CommunicationCreateView.as_view(), name="comm-create"),
    path("public/", CommunicationPublicListView.as_view(), name="comm-public"),
    path("bulk-email/", BulkEmailView.as_view(), name="comm-bulk-email"),
    path("<uuid:id>/", CommunicationDetailView.as_view(), name="comm-detail"),
    path("<uuid:id>/update/", CommunicationUpdateView.as_view(), name="comm-update"),
    path("<uuid:id>/delete/", CommunicationDeleteView.as_view(), name="comm-delete"),
    path("<uuid:id>/status/", CommunicationStatusView.as_view(), name="comm-status"),
    path("<uuid:id>/pdf/", CommunicationPDFView.as_view(), name="comm-pdf"),
    path("<uuid:id>/image/", CommunicationImageView.as_view(), name="comm-image"),
    path("<uuid:id>/share-image/", CommunicationShareImageView.as_view(), name="comm-share-image"),
]
