"""
Tests for Certificate model.
"""
import pytest

from apps.certificates.models import Certificate
from apps.leaders.models import Leader
from apps.users.models import User


@pytest.fixture
def leader(db):
    user = User.objects.create_user(
        email="certlead@example.com",
        password="Pass1234!",
        full_name="Cert Leader",
    )
    return Leader.objects.create(user=user, role="chairman", is_active=True)


@pytest.mark.django_db
class TestCertificateModel:
    def test_create_certificate(self, leader):
        cert = Certificate.objects.create(
            recipient_name="John Doe",
            cert_type="appreciation",
            body="For outstanding service.",
            issued_by=leader,
        )
        assert cert.cert_number.startswith("KCK-CERT-")
        assert cert.verification_url != ""
        assert "verify" in cert.verification_url

    def test_auto_cert_number_unique(self, leader):
        c1 = Certificate.objects.create(
            recipient_name="A", body="Body", issued_by=leader
        )
        c2 = Certificate.objects.create(
            recipient_name="B", body="Body", issued_by=leader
        )
        assert c1.cert_number != c2.cert_number

    def test_str(self, leader):
        cert = Certificate.objects.create(
            recipient_name="Jane", body="Body", issued_by=leader
        )
        assert "Jane" in str(cert)
