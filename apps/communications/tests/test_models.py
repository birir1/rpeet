"""
Tests for Communication model.
"""
import pytest

from apps.communications.models import Communication
from apps.leaders.models import Leader
from apps.users.models import User


@pytest.fixture
def leader(db):
    user = User.objects.create_user(
        email="comm_leader@example.com",
        password="Pass1234!",
        full_name="Comm Leader",
    )
    return Leader.objects.create(user=user, role="secretary", is_active=True)


@pytest.mark.django_db
class TestCommunicationModel:
    def test_create_communication(self, leader):
        comm = Communication.objects.create(
            subject="Test Subject",
            body="<p>Hello world</p>",
            sender=leader,
        )
        assert comm.reference_number.startswith("KCK/")
        assert comm.status == "processing"
        assert comm.audience == "all"

    def test_auto_reference_number(self, leader):
        c1 = Communication.objects.create(subject="First", body="Body", sender=leader)
        c2 = Communication.objects.create(subject="Second", body="Body", sender=leader)
        assert c1.reference_number != c2.reference_number

    def test_str(self, leader):
        comm = Communication.objects.create(subject="Str Test", body="Body", sender=leader)
        assert "Str Test" in str(comm)
