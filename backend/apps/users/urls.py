"""
User URL configuration.
Prefix: /kck/users/
"""
from django.urls import path

from .views import (
    BulkVerifyView,
    UserDeleteView,
    UserDetailView,
    UserExportView,
    UserListView,
    UserMapDataView,
    UserUpdateView,
    UserVerifyView,
)

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("bulk-verify/", BulkVerifyView.as_view(), name="user-bulk-verify"),
    path("export/", UserExportView.as_view(), name="user-export"),
    path("map-data/", UserMapDataView.as_view(), name="user-map-data"),
    path("<uuid:id>/", UserDetailView.as_view(), name="user-detail"),
    path("<uuid:id>/update/", UserUpdateView.as_view(), name="user-update"),
    path("<uuid:id>/verify/", UserVerifyView.as_view(), name="user-verify"),
    path("<uuid:id>/delete/", UserDeleteView.as_view(), name="user-delete"),
]
