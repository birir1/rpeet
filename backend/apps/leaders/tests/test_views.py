"""
Tests for Leader views.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.leaders.models import Leader
from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def chairman_user(db):
    user = User.objects.create_user(
        email="chair@example.com",
        password="Chair123!",
        full_name="Chairman",
    )
    Leader.objects.create(user=user, role="chairman", is_active=True)
    return user


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        email="reg@example.com",
        password="Reg12345!",
        full_name="Regular",
    )


def _auth(client, email, password):
    resp = client.post(reverse("auth-login"), {"email": email, "password": password})
    token = resp.data.get("access") if isinstance(resp.data, dict) else None
    if token:
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.mark.django_db
class TestLeaderEndpoints:
    def test_list_public(self, api_client, chairman_user):
        resp = api_client.get(reverse("leader-list"))
        assert resp.status_code == status.HTTP_200_OK

    def test_create_requires_chairman(self, api_client, regular_user):
        _auth(api_client, "reg@example.com", "Reg12345!")
        resp = api_client.post(reverse("leader-create"), {
            "user": str(regular_user.id),
            "role": "secretary",
        })
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_create_by_chairman(self, api_client, chairman_user, regular_user):
        _auth(api_client, "chair@example.com", "Chair123!")
        resp = api_client.post(reverse("leader-create"), {
            "user": str(regular_user.id),
            "role": "secretary",
        })
        assert resp.status_code == status.HTTP_201_CREATED

    def test_deactivate_leader(self, api_client, chairman_user, regular_user):
        _auth(api_client, "chair@example.com", "Chair123!")
        leader = Leader.objects.create(user=regular_user, role="treasurer", is_active=True)
        resp = api_client.post(reverse("leader-deactivate", kwargs={"id": leader.id}))
        assert resp.status_code == status.HTTP_200_OK
        leader.refresh_from_db()
        assert leader.is_active is False
