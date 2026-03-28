"""
Certificate model for issuing verifiable KCK certificates.
Author: brian korir

I built this model to support the full certificate lifecycle: creation with a
unique cert number, async PDF/image generation (handled in tasks.py), and
public verification via a URL with the cert number embedded. The verification
URL lets anyone confirm a certificate is legitimate by visiting the link or
scanning the QR code printed on the certificate itself.
"""
import uuid

from django.conf import settings
from django.db import models, transaction
from django.db.utils import IntegrityError
from django.utils import timezone

CERT_STATUS_CHOICES = [
    ("draft", "Draft"),
    ("generating", "Generating"),
    ("published", "Published"),
    ("failed", "Failed"),
]

CERT_TYPE_CHOICES = [
    ("appreciation", "Appreciation"),
    ("participation", "Participation"),
    ("leadership", "Leadership"),
    ("welfare", "Welfare"),
    ("custom", "Custom"),
]


class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cert_number = models.CharField(max_length=40, unique=True, blank=True)
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="certificates",
    )
    recipient_name = models.CharField(max_length=120)
    cert_type = models.CharField(max_length=30, choices=CERT_TYPE_CHOICES, default="appreciation")
    body = models.TextField()
    event = models.ForeignKey(
        "events.Event",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="certificates",
    )
    issued_by = models.ForeignKey(
        "leaders.Leader",
        on_delete=models.PROTECT,
        related_name="issued_certificates",
    )
    pdf_file = models.FileField(upload_to="certificates/", blank=True)
    image_file = models.ImageField(upload_to="certificates/", blank=True)
    verification_url = models.CharField(max_length=250, blank=True, default="")
    qr_code = models.ImageField(upload_to="certificates/", blank=True)
    status = models.CharField(max_length=20, choices=CERT_STATUS_CHOICES, default="draft")
    issued_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self):
        return f"{self.cert_number}: {self.recipient_name}"

    def save(self, *args, **kwargs):
        # I use the same atomic-retry pattern as Communication.save() to
        # prevent race conditions on cert_number generation. The retry loop
        # catches IntegrityError from the unique constraint and re-generates
        # with an updated count. The verification_url is derived from the
        # cert_number, so it's generated inside the same atomic block to
        # keep them consistent.
        if not self.cert_number:
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    with transaction.atomic():
                        self.cert_number = self._generate_cert_number()
                        if not self.verification_url:
                            base = getattr(settings, "KCK_BASE_URL", "http://127.0.0.1:8000")
                            self.verification_url = f"{base}/kck/certs/verify/{self.cert_number}/"
                        super().save(*args, **kwargs)
                    return
                except IntegrityError:
                    if attempt == max_retries - 1:
                        raise
                    self.cert_number = ""
                    self.verification_url = ""
        else:
            if not self.verification_url:
                base = getattr(settings, "KCK_BASE_URL", "http://127.0.0.1:8000")
                self.verification_url = f"{base}/kck/certs/verify/{self.cert_number}/"
            super().save(*args, **kwargs)

    @staticmethod
    def _generate_cert_number():
        # Format: KCK-CERT-YEAR-0001 -- I chose hyphens instead of slashes
        # (unlike Communication references) because cert numbers appear in
        # URLs for verification and slashes would break URL routing. The
        # 4-digit zero-padded sequence accommodates higher volume than
        # communications since we issue certificates per-person per-event.
        now = timezone.now()
        year = now.year
        count = (
            Certificate.objects.select_for_update()
            .filter(issued_at__year=year)
            .count()
            + 1
        )
        return f"KCK-CERT-{year}-{count:04d}"
