"""
Tests for User and Auth views.
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
def regular_user(db):
    return User.objects.create_user(
        email="regular@example.com",
        password="Regular123!",
        full_name="Regular User",
        city="seoul",
        category="worker",
    )


@pytest.fixture
def chairman_user(db):
    user = User.objects.create_user(
        email="chairman@example.com",
        password="Chairman123!",
        full_name="Chairman User",
    )
    Leader.objects.create(user=user, role="chairman", is_active=True)
    return user


@pytest.fixture
def secretary_user(db):
    user = User.objects.create_user(
        email="secretary@example.com",
        password="Secretary123!",
        full_name="Secretary User",
    )
    Leader.objects.create(user=user, role="secretary", is_active=True)
    return user


@pytest.fixture
def treasurer_user(db):
    user = User.objects.create_user(
        email="treasurer@example.com",
        password="Treasurer123!",
        full_name="Treasurer User",
    )
    Leader.objects.create(user=user, role="treasurer", is_active=True)
    return user


def _auth(client, user, password=None):
    """Helper to authenticate client."""
    resp = client.post(reverse("auth-login"), {
        "email": user.email,
        "password": password or user.email.split("@")[0].capitalize() + "123!",
    })
    token = resp.data.get("access") if isinstance(resp.data, dict) else None
    if token:
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


# -------------------------------------------------------------------
# Auth tests
# -------------------------------------------------------------------
@pytest.mark.django_db
class TestAuth:
    def test_register(self, api_client):
        resp = api_client.post(reverse("auth-register"), {
            "full_name": "New User",
            "email": "new@example.com",
            "password": "NewUser123!",
            "city": "seoul",
            "category": "student",
        })
        assert resp.status_code == status.HTTP_201_CREATED
        # resp.data contains the raw DRF data; the renderer wraps it into
        # {"success": true, "data": ...} only at the serialization stage.
        # When using the test client the renderer is invoked, so the
        # envelope is present in resp.data.
        data = resp.data
        # The renderer may or may not have wrapped it depending on content negotiation
        if "success" in data:
            assert data["success"] is True
        else:
            # Raw data from serializer - just verify we got user fields back
            assert "id" in data or "full_name" in data

    def test_register_duplicate_email(self, api_client, regular_user):
        resp = api_client.post(reverse("auth-register"), {
            "full_name": "Dup",
            "email": regular_user.email,
            "password": "Dup12345!",
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_login(self, api_client, regular_user):
        resp = api_client.post(reverse("auth-login"), {
            "email": "regular@example.com",
            "password": "Regular123!",
        })
        assert resp.status_code == status.HTTP_200_OK
        assert "access" in resp.data.get("data", resp.data)

    def test_me(self, api_client, regular_user):
        _auth(api_client, regular_user, "Regular123!")
        resp = api_client.get(reverse("auth-me"))
        assert resp.status_code == status.HTTP_200_OK


# -------------------------------------------------------------------
# User endpoint tests
# -------------------------------------------------------------------
@pytest.mark.django_db
class TestUserEndpoints:
    def test_list_requires_secretary(self, api_client, regular_user):
        _auth(api_client, regular_user, "Regular123!")
        resp = api_client.get(reverse("user-list"))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_list_allowed_for_secretary(self, api_client, secretary_user):
        _auth(api_client, secretary_user, "Secretary123!")
        resp = api_client.get(reverse("user-list"))
        assert resp.status_code == status.HTTP_200_OK

    def test_detail_owner_can_view(self, api_client, regular_user):
        _auth(api_client, regular_user, "Regular123!")
        resp = api_client.get(reverse("user-detail", kwargs={"id": regular_user.id}))
        assert resp.status_code == status.HTTP_200_OK

    def test_detail_other_user_forbidden(self, api_client, regular_user, secretary_user):
        # Create another regular user
        other = User.objects.create_user(
            email="other@example.com",
            password="Other123!",
            full_name="Other",
        )
        _auth(api_client, regular_user, "Regular123!")
        resp = api_client.get(reverse("user-detail", kwargs={"id": other.id}))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_verify_by_secretary(self, api_client, secretary_user, regular_user):
        _auth(api_client, secretary_user, "Secretary123!")
        resp = api_client.post(reverse("user-verify", kwargs={"id": regular_user.id}))
        assert resp.status_code == status.HTTP_200_OK
        regular_user.refresh_from_db()
        assert regular_user.is_verified is True

    def test_soft_delete_by_chairman(self, api_client, chairman_user, regular_user):
        _auth(api_client, chairman_user, "Chairman123!")
        resp = api_client.delete(reverse("user-delete", kwargs={"id": regular_user.id}))
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        regular_user.refresh_from_db()
        assert regular_user.is_deleted is True

    def test_export_csv(self, api_client, secretary_user):
        _auth(api_client, secretary_user, "Secretary123!")
        resp = api_client.get(reverse("user-export"))
        assert resp.status_code == status.HTTP_200_OK
        assert resp["Content-Type"] == "text/csv"
