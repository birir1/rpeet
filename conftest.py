"""
Root conftest for pytest-django -- shared test fixtures.
Author: Meshack Tirop

I centralize factory fixtures here so every test module can create users and
leaders without duplicating setup logic. The make_user and make_leader fixtures
use a factory pattern (returning callables) so tests can create multiple
instances with different parameters in a single test case.
"""
import pytest
from rest_framework.test import APIClient

from apps.leaders.models import Leader
from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def make_user(db):
    """Factory fixture to create users."""
    def _make_user(
        email,
        password="TestPass123!",
        full_name="Test User",
        **kwargs,
    ):
        return User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            **kwargs,
        )
    return _make_user


@pytest.fixture
def make_leader(db, make_user):
    """Factory fixture to create leader users."""
    def _make_leader(role, email=None, **user_kwargs):
        import uuid
        if email is None:
            email = f"{role}-{uuid.uuid4().hex[:6]}@test.com"
        user = make_user(email=email, **user_kwargs)
        leader = Leader.objects.create(user=user, role=role, is_active=True)
        return user, leader
    return _make_leader
