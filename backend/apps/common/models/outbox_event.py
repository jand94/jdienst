from django.db import models
from django.utils import timezone

from .base_model import TimeStampedModel, UUIDPrimaryKeyModel


class OutboxEvent(UUIDPrimaryKeyModel, TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    )

    topic = models.CharField(max_length=128, db_index=True)
    dedup_key = models.CharField(max_length=255, blank=True, default="", db_index=True)
    payload = models.JSONField(default=dict)
    headers = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    attempts = models.PositiveIntegerField(default=0)
    next_attempt_at = models.DateTimeField(db_index=True, default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_error = models.TextField(blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=("status", "next_attempt_at"), name="common_outb_status_3cd8ae_idx"),
            models.Index(fields=("topic", "status"), name="common_outb_topic_b2f2b1_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("topic", "dedup_key"),
                condition=~models.Q(dedup_key=""),
                name="common_outbox_topic_dedup_unique",
            )
        ]

    def __str__(self) -> str:
        return f"{self.topic} ({self.status})"
