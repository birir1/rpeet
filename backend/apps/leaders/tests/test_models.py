"""
Tests for Leader model.
"""
import uuid

import pytest

from apps.leaders.models import Leader
from apps.users.models import User


@pytest.mark.django_db
class TestLeaderModel:
    def test_create_leader(self):
        user = User.objects.create_user(
            email="lead@example.com",
            password="Lead1234!",
            full_name="Lead User",
        )
        leader = Leader.objects.create(user=user, role="chairman")
        assert isinstance(leader.id, uuid.UUID)
        assert leader.is_active is True
        assert str(leader) == "Lead User (Chairman)"

    def test_leader_roles(self):
        roles = ["chairman", "secretary", "treasurer", "welfare", "committee"]
        for i, role in enumerate(roles):
            user = User.objects.create_user(
                email=f"role{i}@example.com",
                password="Pass1234!",
                full_name=f"Role {i}",
            )
            leader = Leader.objects.create(user=user, role=role)
            assert leader.role == role

    def test_one_to_one_constraint(self):
        user = User.objects.create_user(
            email="oto@example.com",
            password="Pass1234!",
            full_name="OTO User",
        )
        Leader.objects.create(user=user, role="secretary")
        with pytest.raises(Exception):
            Leader.objects.create(user=user, role="treasurer")
