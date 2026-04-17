from django.conf import settings
from django.db import models

from .base_model import TimeStampedModel, UUIDPrimaryKeyModel


class IdempotencyKey(UUIDPrimaryKeyModel, TimeStampedModel):
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = (
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    )

    scope = models.CharField(max_length=128, db_index=True)
    key = models.CharField(max_length=255)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="idempotency_keys",
    )
    actor_identifier = models.CharField(max_length=64, db_index=True)
    request_fingerprint = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_IN_PROGRESS, db_index=True)
    response_code = models.PositiveSmallIntegerField(null=True, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    error_payload = models.JSONField(default=dict, blank=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("scope", "key", "actor_identifier"),
                name="common_idempotency_scope_key_actor_unique",
            )
        ]
        indexes = [
            models.Index(fields=("scope", "status", "expires_at"), name="common_idem_scope_33458a_idx"),
            models.Index(fields=("expires_at",), name="common_idem_expires_18f86f_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.scope}:{self.key} ({self.status})"
