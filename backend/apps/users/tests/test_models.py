"""
Tests for User and Membership models.
"""
import uuid
from datetime import date, timedelta

import pytest
from django.utils import timezone

from apps.users.models import AuditLog, Membership, User


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            full_name="Test User",
        )
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_deleted is False
        assert user.id is not None

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
        )
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_email_required(self):
        with pytest.raises(ValueError, match="Email is required"):
            User.objects.create_user(email="", password="pass")

    def test_soft_delete(self):
        user = User.objects.create_user(
            email="del@example.com", password="pass", full_name="Del"
        )
        user.soft_delete()
        user.refresh_from_db()
        assert user.is_deleted is True
        assert user.is_active is False
        assert user.deleted_at is not None

    def test_uuid_pk(self):
        user = User.objects.create_user(
            email="uuid@example.com", password="pass", full_name="Uuid"
        )
        assert isinstance(user.id, uuid.UUID)

    def test_membership_status_property(self):
        user = User.objects.create_user(
            email="mem@example.com", password="pass", full_name="Mem"
        )
        assert user.membership_status is None
        Membership.objects.create(
            user=user, status="active", start_date=date.today(), fee_amount=50000
        )
        assert user.membership_status == "active"


@pytest.mark.django_db
class TestMembershipModel:
    def test_auto_expiry_date(self):
        user = User.objects.create_user(
            email="exp@example.com", password="pass", full_name="Exp"
        )
        start = date(2025, 1, 1)
        m = Membership.objects.create(user=user, start_date=start, fee_amount=50000)
        assert m.expiry_date == start + timedelta(days=365)

    def test_membership_defaults(self):
        user = User.objects.create_user(
            email="def@example.com", password="pass", full_name="Def"
        )
        m = Membership.objects.create(user=user, start_date=date.today(), fee_amount=50000)
        assert m.status == "pending"
        assert m.currency == "KRW"


@pytest.mark.django_db
class TestAuditLogModel:
    def test_create_audit_log(self):
        uid = uuid.uuid4()
        log = AuditLog.objects.create(
            action="created",
            model_type="User",
            model_id=uid,
            new_values={"email": "test@test.com"},
        )
        assert log.id is not None
        assert log.action == "created"
        assert log.model_id == uid
