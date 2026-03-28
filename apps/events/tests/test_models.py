"""
Tests for Event model.
"""
from datetime import date

import pytest

from apps.events.models import Event
from apps.leaders.models import Leader
from apps.users.models import User


@pytest.fixture
def leader(db):
    user = User.objects.create_user(
        email="evtlead@example.com",
        password="Pass1234!",
        full_name="Event Leader",
    )
    return Leader.objects.create(user=user, role="committee", is_active=True)


@pytest.mark.django_db
class TestEventModel:
    def test_create_event(self, leader):
        event = Event.objects.create(
            title="Independence Day Celebration",
            event_date=date(2025, 12, 12),
            created_by=leader,
        )
        assert event.slug == "independence-day-celebration"
        assert event.is_published is False

    def test_auto_slug_unique(self, leader):
        Event.objects.create(title="Meetup", event_date=date(2025, 1, 1), created_by=leader)
        e2 = Event.objects.create(title="Meetup", event_date=date(2025, 2, 1), created_by=leader)
        assert e2.slug == "meetup-1"

    def test_str(self, leader):
        event = Event.objects.create(
            title="BBQ Party", event_date=date(2025, 6, 1), created_by=leader
        )
        assert str(event) == "BBQ Party"
