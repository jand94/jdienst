from django.db import models

from .base_model import TimeStampedModel


class DistributedLock(TimeStampedModel):
    key = models.CharField(max_length=128, unique=True)
    owner = models.CharField(max_length=128)
    token = models.CharField(max_length=128)
    fencing_counter = models.BigIntegerField(default=0)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=("expires_at",), name="common_dlock_exp_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.key} ({self.owner})"
