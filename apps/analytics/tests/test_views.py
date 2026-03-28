"""
Tests for Analytics views.
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
        email="anch@example.com",
        password="AnCh1234!",
        full_name="Analytics Chairman",
    )
    Leader.objects.create(user=user, role="chairman", is_active=True)
    return user


@pytest.fixture
def secretary_user(db):
    user = User.objects.create_user(
        email="ansec@example.com",
        password="AnSec123!",
        full_name="Analytics Secretary",
    )
    Leader.objects.create(user=user, role="secretary", is_active=True)
    return user


@pytest.fixture
def treasurer_user(db):
    user = User.objects.create_user(
        email="antr@example.com",
        password="AnTr1234!",
        full_name="Analytics Treasurer",
    )
    Leader.objects.create(user=user, role="treasurer", is_active=True)
    return user


def _auth(client, email, password):
    resp = client.post(reverse("auth-login"), {"email": email, "password": password})
    token = resp.data.get("access") if isinstance(resp.data, dict) else None
    if token:
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.mark.django_db
class TestAnalyticsEndpoints:
    def test_overview_public(self, api_client):
        resp = api_client.get(reverse("analytics-overview"))
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data.get("data", resp.data)
        assert "total_members" in data

    def test_overview_chairman_extended(self, api_client, chairman_user):
        _auth(api_client, "anch@example.com", "AnCh1234!")
        resp = api_client.get(reverse("analytics-overview"))
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data.get("data", resp.data)
        assert "active_memberships" in data

    def test_cities_requires_secretary(self, api_client):
        resp = api_client.get(reverse("analytics-cities"))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cities_secretary(self, api_client, secretary_user):
        _auth(api_client, "ansec@example.com", "AnSec123!")
        resp = api_client.get(reverse("analytics-cities"))
        assert resp.status_code == status.HTTP_200_OK

    def test_categories_secretary(self, api_client, secretary_user):
        _auth(api_client, "ansec@example.com", "AnSec123!")
        resp = api_client.get(reverse("analytics-categories"))
        assert resp.status_code == status.HTTP_200_OK

    def test_membership_requires_treasurer(self, api_client, secretary_user):
        _auth(api_client, "ansec@example.com", "AnSec123!")
        resp = api_client.get(reverse("analytics-membership"))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_membership_treasurer(self, api_client, treasurer_user):
        _auth(api_client, "antr@example.com", "AnTr1234!")
        resp = api_client.get(reverse("analytics-membership"))
        assert resp.status_code == status.HTTP_200_OK
