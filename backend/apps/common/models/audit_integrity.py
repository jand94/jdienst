from django.db import models

from .audit_event import AuditEvent
from .base_model import TimeStampedModel, UUIDPrimaryKeyModel


class AuditIntegrityCheckpoint(UUIDPrimaryKeyModel, TimeStampedModel):
    sequence = models.PositiveIntegerField(unique=True, db_index=True)
    anchor_event = models.ForeignKey(
        AuditEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="integrity_checkpoints",
    )
    anchor_hash = models.CharField(max_length=64, db_index=True)
    signature = models.CharField(max_length=128)
    signer = models.CharField(max_length=64, default="hmac-sha256")
    metadata = models.JSONField(default=dict, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-sequence",)

    def __str__(self) -> str:
        return f"Checkpoint #{self.sequence} ({self.anchor_hash[:12]})"


class AuditIntegrityVerification(UUIDPrimaryKeyModel, TimeStampedModel):
    STATUS_PASSED = "passed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = (
        (STATUS_PASSED, "Passed"),
        (STATUS_FAILED, "Failed"),
    )

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, db_index=True)
    checked_events = models.PositiveIntegerField(default=0)
    last_event_hash = models.CharField(max_length=64, blank=True, default="")
    checkpoint = models.ForeignKey(
        AuditIntegrityCheckpoint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verifications",
    )
    details = models.JSONField(default=dict, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Integrity verification ({self.status})"
