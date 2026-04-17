from django.db import models

from .base_model import UUIDPrimaryKeyModel
from .soft_delete_model import SoftDeleteModel


class Tenant(UUIDPrimaryKeyModel, SoftDeleteModel):
    STATUS_ACTIVE = "active"
    STATUS_SUSPENDED = "suspended"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_SUSPENDED, "Suspended"),
        (STATUS_ARCHIVED, "Archived"),
    )

    slug = models.SlugField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE, db_index=True)
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=("status", "slug"), name="common_tnt_stat_slug_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.slug} ({self.status})"
