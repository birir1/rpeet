"""
Tests for Certificate views.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.certificates.models import Certificate
from apps.leaders.models import Leader
from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def chairman_user(db):
    user = User.objects.create_user(
        email="certchair@example.com",
        password="Chair123!",
        full_name="Cert Chairman",
    )
    Leader.objects.create(user=user, role="chairman", is_active=True)
    return user


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        email="certreg@example.com",
        password="CertReg1!",
        full_name="Cert Regular",
    )


def _auth(client, email, password):
    resp = client.post(reverse("auth-login"), {"email": email, "password": password})
    token = resp.data.get("access") if isinstance(resp.data, dict) else None
    if token:
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.mark.django_db
class TestCertificateEndpoints:
    def test_list_requires_leader(self, api_client, regular_user):
        _auth(api_client, "certreg@example.com", "CertReg1!")
        resp = api_client.get(reverse("cert-list"))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_create_by_leader(self, api_client, chairman_user):
        _auth(api_client, "certchair@example.com", "Chair123!")
        resp = api_client.post(reverse("cert-create"), {
            "recipient_name": "Test Recipient",
            "cert_type": "appreciation",
            "body": "For great work.",
        })
        assert resp.status_code == status.HTTP_201_CREATED

    def test_verify_public(self, api_client, chairman_user):
        leader = chairman_user.leader
        cert = Certificate.objects.create(
            recipient_name="Public Verify",
            body="Body",
            issued_by=leader,
        )
        resp = api_client.get(reverse("cert-verify", kwargs={"cert_number": cert.cert_number}))
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data.get("data", resp.data)
        assert data.get("valid") is True

    def test_verify_not_found(self, api_client):
        resp = api_client.get(reverse("cert-verify", kwargs={"cert_number": "FAKE-0000"}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_mine(self, api_client, regular_user, chairman_user):
        leader = chairman_user.leader
        Certificate.objects.create(
            recipient_user=regular_user,
            recipient_name=regular_user.full_name,
            body="Body",
            issued_by=leader,
        )
        _auth(api_client, "certreg@example.com", "CertReg1!")
        resp = api_client.get(reverse("cert-mine"))
        assert resp.status_code == status.HTTP_200_OK
