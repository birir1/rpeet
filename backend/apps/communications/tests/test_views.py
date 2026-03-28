"""
Tests for Communication views.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.communications.models import Communication
from apps.leaders.models import Leader
from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def secretary_user(db):
    user = User.objects.create_user(
        email="csec@example.com",
        password="Csec1234!",
        full_name="Comm Secretary",
    )
    Leader.objects.create(user=user, role="secretary", is_active=True)
    return user


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        email="creg@example.com",
        password="Creg1234!",
        full_name="Comm Regular",
    )


def _auth(client, email, password):
    resp = client.post(reverse("auth-login"), {"email": email, "password": password})
    token = resp.data.get("access") if isinstance(resp.data, dict) else None
    if token:
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.mark.django_db
class TestCommunicationEndpoints:
    def test_list_requires_auth(self, api_client):
        resp = api_client.get(reverse("comm-list"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_authenticated(self, api_client, regular_user):
        _auth(api_client, "creg@example.com", "Creg1234!")
        resp = api_client.get(reverse("comm-list"))
        assert resp.status_code == status.HTTP_200_OK

    def test_create_requires_leader(self, api_client, regular_user):
        _auth(api_client, "creg@example.com", "Creg1234!")
        resp = api_client.post(reverse("comm-create"), {
            "subject": "Test",
            "body": "Hello",
            "category": "general",
            "audience": "all",
        })
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_create_by_leader(self, api_client, secretary_user):
        _auth(api_client, "csec@example.com", "Csec1234!")
        resp = api_client.post(reverse("comm-create"), {
            "subject": "Important Notice",
            "body": "<p>Please note</p>",
            "category": "general",
            "audience": "all",
        })
        assert resp.status_code == status.HTTP_201_CREATED

    def test_public_list(self, api_client, secretary_user):
        leader = secretary_user.leader
        Communication.objects.create(
            subject="Public Comm",
            body="Body",
            sender=leader,
            status="published",
            audience="all",
        )
        resp = api_client.get(reverse("comm-public"))
        assert resp.status_code == status.HTTP_200_OK
