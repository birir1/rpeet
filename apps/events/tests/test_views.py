"""
Tests for Event views.
"""
from datetime import date

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.events.models import Event
from apps.leaders.models import Leader
from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def committee_user(db):
    user = User.objects.create_user(
        email="evtcomm@example.com",
        password="EvtComm1!",
        full_name="Event Committee",
    )
    Leader.objects.create(user=user, role="committee", is_active=True)
    return user


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        email="evtreg@example.com",
        password="EvtReg1!",
        full_name="Event Regular",
    )


def _auth(client, email, password):
    resp = client.post(reverse("auth-login"), {"email": email, "password": password})
    token = resp.data.get("access") if isinstance(resp.data, dict) else None
    if token:
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.mark.django_db
class TestEventEndpoints:
    def test_list_public(self, api_client, committee_user):
        leader = committee_user.leader
        Event.objects.create(
            title="Published Event",
            event_date=date(2025, 6, 1),
            created_by=leader,
            is_published=True,
        )
        resp = api_client.get(reverse("event-list"))
        assert resp.status_code == status.HTTP_200_OK

    def test_detail_by_slug(self, api_client, committee_user):
        leader = committee_user.leader
        event = Event.objects.create(
            title="Slug Test Event",
            event_date=date(2025, 7, 1),
            created_by=leader,
            is_published=True,
        )
        resp = api_client.get(reverse("event-detail", kwargs={"slug": event.slug}))
        assert resp.status_code == status.HTTP_200_OK

    def test_create_requires_committee(self, api_client, regular_user):
        _auth(api_client, "evtreg@example.com", "EvtReg1!")
        resp = api_client.post(reverse("event-create"), {
            "title": "New Event",
            "event_date": "2025-08-01",
        })
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_create_by_committee(self, api_client, committee_user):
        _auth(api_client, "evtcomm@example.com", "EvtComm1!")
        resp = api_client.post(reverse("event-create"), {
            "title": "New Event",
            "event_date": "2025-08-01",
        })
        assert resp.status_code == status.HTTP_201_CREATED

    def test_publish_event(self, api_client, committee_user):
        _auth(api_client, "evtcomm@example.com", "EvtComm1!")
        leader = committee_user.leader
        event = Event.objects.create(
            title="To Publish",
            event_date=date(2025, 9, 1),
            created_by=leader,
        )
        resp = api_client.post(reverse("event-publish", kwargs={"id": event.id}))
        assert resp.status_code == status.HTTP_200_OK
        event.refresh_from_db()
        assert event.is_published is True
