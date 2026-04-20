from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import AuditFieldsModel, TenantAwareModel, UUIDPrimaryKeyModel


class Task(UUIDPrimaryKeyModel, TenantAwareModel, AuditFieldsModel):
    STATUS_OPEN = "open"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_DONE = "done"
    STATUS_CHOICES = (
        (STATUS_OPEN, "Open"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_DONE, "Done"),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OPEN, db_index=True)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fetests_tasks_assigned",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fetests_tasks_assigned_by",
    )
    due_at = models.DateTimeField(null=True, blank=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=("tenant", "status", "-created_at"), name="fetests_task_tenant_status_idx"),
            models.Index(fields=("tenant", "assignee", "-updated_at"), name="fet_tsk_tnt_asg_upd_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.status})"
