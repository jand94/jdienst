from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base_model import TimeStampedModel, UUIDPrimaryKeyModel


class AuditEvent(UUIDPrimaryKeyModel, TimeStampedModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    action = models.CharField(max_length=128, db_index=True)
    target_model = models.CharField(max_length=128, db_index=True)
    target_id = models.CharField(max_length=64, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default="")
    previous_hash = models.CharField(max_length=64, blank=True, default="")
    integrity_hash = models.CharField(max_length=64, editable=False, db_index=True, default="")
    archived_at = models.DateTimeField(null=True, blank=True, db_index=True)
    exported_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["target_model", "target_id"]),
            models.Index(fields=["action", "created_at"]),
        ]
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.action} on {self.target_model}:{self.target_id}"

    def save(self, *args, **kwargs):
        if self.pk and self.__class__.objects.filter(pk=self.pk).exists():
            raise ValidationError("AuditEvent is append-only and cannot be updated.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("AuditEvent is append-only and cannot be deleted.")
