"""
Certificate URL configuration.
Prefix: /kck/certs/
"""
from django.urls import path

from .views import (
    CertificateCreateView,
    CertificateDetailView,
    CertificateImageView,
    CertificateListView,
    CertificateMineView,
    CertificatePDFView,
    CertificateStatusView,
    CertificateVerifyView,
)

urlpatterns = [
    path("", CertificateListView.as_view(), name="cert-list"),
    path("create/", CertificateCreateView.as_view(), name="cert-create"),
    path("mine/", CertificateMineView.as_view(), name="cert-mine"),
    path("verify/<str:cert_number>/", CertificateVerifyView.as_view(), name="cert-verify"),
    path("<uuid:id>/", CertificateDetailView.as_view(), name="cert-detail"),
    path("<uuid:id>/status/", CertificateStatusView.as_view(), name="cert-status"),
    path("<uuid:id>/pdf/", CertificatePDFView.as_view(), name="cert-pdf"),
    path("<uuid:id>/image/", CertificateImageView.as_view(), name="cert-image"),
]
