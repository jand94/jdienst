from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from .base_model import TimeStampedModel


class SoftDeleteQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted_at__isnull=True)

    def deleted(self):
        return self.filter(deleted_at__isnull=False)

    def soft_delete(self, *, actor=None, reason: str = "") -> int:
        return self.active().update(
            deleted_at=timezone.now(),
            deleted_by=actor if getattr(actor, "is_authenticated", False) else None,
            delete_reason=reason,
            updated_at=timezone.now(),
        )

    def restore(self) -> int:
        return self.deleted().update(
            deleted_at=None,
            deleted_by=None,
            delete_reason="",
            updated_at=timezone.now(),
        )

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        return super().delete()


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).active()


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class DeletedObjectsManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()


class SoftDeleteModel(TimeStampedModel):
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_deleted",
    )
    delete_reason = models.CharField(max_length=255, blank=True, default="")

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()
    deleted_objects = DeletedObjectsManager()

    class Meta:
        abstract = True

    def soft_delete(self, *, actor=None, reason: str = "") -> None:
        self.deleted_at = timezone.now()
        self.deleted_by = actor if getattr(actor, "is_authenticated", False) else None
        self.delete_reason = reason
        self.save(update_fields=("deleted_at", "deleted_by", "delete_reason", "updated_at"))

    def restore(self) -> None:
        self.deleted_at = None
        self.deleted_by = None
        self.delete_reason = ""
        self.save(update_fields=("deleted_at", "deleted_by", "delete_reason", "updated_at"))

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        return super().delete()
