"""
Analytics models - includes SiteSetting for dynamic configuration.
Author: Meshack Tirop
"""
import uuid

from django.db import models


class SiteSetting(models.Model):
    """Key-value store for site-wide settings (e.g. membership fee).

    I chose this key-value pattern over hardcoded settings or environment
    variables because the chairman needs to update values like the membership
    fee amount at runtime without a code deployment. A dedicated settings model
    per value would mean a migration every time we add a new configurable, so
    a generic JSONField-backed store keeps things flexible -- any new setting
    is just a new row, no schema change required.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return f"SiteSetting({self.key})"
