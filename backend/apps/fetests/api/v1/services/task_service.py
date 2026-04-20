from __future__ import annotations

from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.common.api.v1.services import (
    ensure_user_in_tenant,
    record_audit_event,
    tenant_scoped_queryset,
)
from apps.common.exceptions import ValidationError
from apps.common.models import Tenant, TenantMembership
from apps.fetests.models import Task
from apps.notification.api.v1.services import create_notification
from apps.notification.models import NotificationType, UserNotificationPreference

User = get_user_model()

_TASK_ASSIGNED_TYPE_KEY = "fetests-task-assigned"
_TASK_UPDATED_TYPE_KEY = "fetests-task-updated"
_TASK_COMPLETED_TYPE_KEY = "fetests-task-completed"


def list_tasks_for_tenant(*, tenant: Tenant):
    return tenant_scoped_queryset(
        queryset=Task.objects.select_related("assignee", "assigned_by", "created_by", "updated_by"),
        tenant=tenant,
    ).order_by("-created_at")


def _resolve_tenant_member(*, tenant: Tenant, user_id: int | None):
    if user_id is None:
        return None
    user = User.objects.filter(pk=user_id).first()
    if user is None:
        raise ValidationError("Assignee does not exist.")
    membership_exists = TenantMembership.objects.filter(tenant=tenant, user=user, is_active=True).exists()
    if not membership_exists:
        raise ValidationError("Assignee must be an active tenant member.")
    return user


def _ensure_notification_type(
    *,
    key: str,
    title: str,
    description: str,
    allow_user_opt_out: bool,
) -> NotificationType:
    notification_type, _ = NotificationType.objects.get_or_create(
        key=key,
        defaults={
            "title": title,
            "description": description,
            "default_channels": [
                UserNotificationPreference.CHANNEL_IN_APP,
                UserNotificationPreference.CHANNEL_REALTIME,
            ],
            "allow_user_opt_out": allow_user_opt_out,
            "is_active": True,
        },
    )
    return notification_type


def _notify_recipients(
    *,
    tenant: Tenant,
    actor,
    recipients: list,
    notification_type_key: str,
    title: str,
    body: str,
    metadata: dict,
    dedup_key_prefix: str,
    request_id: str | None,
    trace_id: str | None,
) -> None:
    sent_recipient_ids: set[int] = set()
    for recipient in recipients:
        if recipient is None:
            continue
        if recipient.pk in sent_recipient_ids:
            continue
        sent_recipient_ids.add(recipient.pk)
        create_notification(
            tenant=tenant,
            actor=actor,
            recipient=recipient,
            notification_type_key=notification_type_key,
            title=title,
            body=body,
            metadata=metadata,
            dedup_key=f"{dedup_key_prefix}:{recipient.pk}:{uuid4()}",
            channels=None,
            request_id=request_id,
            trace_id=trace_id,
        )


@transaction.atomic
def create_task(
    *,
    tenant: Tenant,
    actor,
    title: str,
    description: str,
    assignee_id: int | None,
    due_at,
    source: str,
    request_id: str | None = None,
    trace_id: str | None = None,
) -> Task:
    ensure_user_in_tenant(user=actor, tenant=tenant)
    assignee = _resolve_tenant_member(tenant=tenant, user_id=assignee_id)

    task = Task.objects.create(
        tenant=tenant,
        title=title,
        description=description,
        status=Task.STATUS_IN_PROGRESS if assignee else Task.STATUS_OPEN,
        assignee=assignee,
        assigned_by=actor if assignee else None,
        due_at=due_at,
        created_by=actor,
        updated_by=actor,
    )
    record_audit_event(
        action="fetests.task.created",
        target_model="fetests.Task",
        target_id=str(task.pk),
        actor=actor,
        metadata={
            "source": source,
            "tenant_id": str(tenant.pk),
            "assignee_id": str(assignee.pk) if assignee else None,
        },
        request_id=request_id,
        trace_id=trace_id,
    )

    if assignee is not None:
        notification_type = _ensure_notification_type(
            key=_TASK_ASSIGNED_TYPE_KEY,
            title="Task zugewiesen",
            description="Info ueber eine neue Task-Zuweisung.",
            allow_user_opt_out=True,
        )
        _notify_recipients(
            tenant=tenant,
            actor=actor,
            recipients=[assignee],
            notification_type_key=notification_type.key,
            title=f"Neue Aufgabe: {task.title}",
            body=f"Dir wurde die Aufgabe '{task.title}' zugewiesen.",
            metadata={
                "source": source,
                "event": "task_created_with_assignment",
                "task_id": str(task.pk),
                "status": task.status,
            },
            dedup_key_prefix=f"fetests.task.assigned:{task.pk}",
            request_id=request_id,
            trace_id=trace_id,
        )
    return task


@transaction.atomic
def assign_task(
    *,
    task: Task,
    tenant: Tenant,
    actor,
    assignee_id: int,
    source: str,
    request_id: str | None = None,
    trace_id: str | None = None,
) -> Task:
    ensure_user_in_tenant(user=actor, tenant=tenant)
    if task.tenant_id != tenant.pk:
        raise ValidationError("Task does not belong to tenant scope.")

    assignee = _resolve_tenant_member(tenant=tenant, user_id=assignee_id)
    previous_assignee_id = task.assignee_id
    task.assignee = assignee
    task.assigned_by = actor
    if task.status == Task.STATUS_OPEN:
        task.status = Task.STATUS_IN_PROGRESS
    task.updated_by = actor
    task.save(update_fields=("assignee", "assigned_by", "status", "updated_by", "updated_at"))

    record_audit_event(
        action="fetests.task.assigned",
        target_model="fetests.Task",
        target_id=str(task.pk),
        actor=actor,
        metadata={
            "source": source,
            "previous_assignee_id": str(previous_assignee_id) if previous_assignee_id else None,
            "assignee_id": str(assignee.pk),
        },
        request_id=request_id,
        trace_id=trace_id,
    )
    notification_type = _ensure_notification_type(
        key=_TASK_ASSIGNED_TYPE_KEY,
        title="Task zugewiesen",
        description="Info ueber eine neue Task-Zuweisung.",
        allow_user_opt_out=True,
    )
    _notify_recipients(
        tenant=tenant,
        actor=actor,
        recipients=[assignee],
        notification_type_key=notification_type.key,
        title=f"Task aktualisiert: {task.title}",
        body=f"Du bist jetzt fuer die Aufgabe '{task.title}' zustaendig.",
        metadata={
            "source": source,
            "event": "task_assigned",
            "task_id": str(task.pk),
            "status": task.status,
        },
        dedup_key_prefix=f"fetests.task.assigned:{task.pk}",
        request_id=request_id,
        trace_id=trace_id,
    )
    return task


@transaction.atomic
def update_task(
    *,
    task: Task,
    tenant: Tenant,
    actor,
    title: str | None,
    description: str | None,
    due_at,
    source: str,
    request_id: str | None = None,
    trace_id: str | None = None,
) -> Task:
    ensure_user_in_tenant(user=actor, tenant=tenant)
    if task.tenant_id != tenant.pk:
        raise ValidationError("Task does not belong to tenant scope.")
    if task.status == Task.STATUS_DONE:
        raise ValidationError("Completed tasks cannot be updated.")

    changed_fields: dict[str, dict[str, str | None]] = {}
    if title is not None and task.title != title:
        changed_fields["title"] = {"old": task.title, "new": title}
        task.title = title
    if description is not None and task.description != description:
        changed_fields["description"] = {"old": task.description, "new": description}
        task.description = description
    if due_at is not None and task.due_at != due_at:
        changed_fields["due_at"] = {"old": str(task.due_at), "new": str(due_at)}
        task.due_at = due_at

    if not changed_fields:
        return task

    task.updated_by = actor
    task.save(update_fields=tuple(changed_fields.keys()) + ("updated_by", "updated_at"))
    record_audit_event(
        action="fetests.task.updated",
        target_model="fetests.Task",
        target_id=str(task.pk),
        actor=actor,
        metadata={
            "source": source,
            "changes": changed_fields,
        },
        request_id=request_id,
        trace_id=trace_id,
    )
    notification_type = _ensure_notification_type(
        key=_TASK_UPDATED_TYPE_KEY,
        title="Task aktualisiert",
        description="Info ueber Aenderungen an einer Task.",
        allow_user_opt_out=True,
    )
    recipient = task.assignee if task.assignee is not None else actor
    _notify_recipients(
        tenant=tenant,
        actor=actor,
        recipients=[recipient],
        notification_type_key=notification_type.key,
        title=f"Aufgabe aktualisiert: {task.title}",
        body=f"An der Aufgabe '{task.title}' wurden Details geaendert.",
        metadata={
            "source": source,
            "event": "task_updated",
            "task_id": str(task.pk),
            "changed_fields": sorted(changed_fields.keys()),
        },
        dedup_key_prefix=f"fetests.task.updated:{task.pk}",
        request_id=request_id,
        trace_id=trace_id,
    )
    return task


@transaction.atomic
def complete_task(
    *,
    task: Task,
    tenant: Tenant,
    actor,
    source: str,
    request_id: str | None = None,
    trace_id: str | None = None,
) -> Task:
    ensure_user_in_tenant(user=actor, tenant=tenant)
    if task.tenant_id != tenant.pk:
        raise ValidationError("Task does not belong to tenant scope.")
    if task.status == Task.STATUS_DONE:
        return task

    task.status = Task.STATUS_DONE
    task.completed_at = timezone.now()
    task.updated_by = actor
    task.save(update_fields=("status", "completed_at", "updated_by", "updated_at"))
    record_audit_event(
        action="fetests.task.completed",
        target_model="fetests.Task",
        target_id=str(task.pk),
        actor=actor,
        metadata={
            "source": source,
            "assignee_id": str(task.assignee_id) if task.assignee_id else None,
            "assigned_by_id": str(task.assigned_by_id) if task.assigned_by_id else None,
        },
        request_id=request_id,
        trace_id=trace_id,
    )
    notification_type = _ensure_notification_type(
        key=_TASK_COMPLETED_TYPE_KEY,
        title="Task erledigt",
        description="Info ueber eine abgeschlossene Task.",
        allow_user_opt_out=True,
    )
    recipients = [task.assignee, task.assigned_by, actor]
    _notify_recipients(
        tenant=tenant,
        actor=actor,
        recipients=recipients,
        notification_type_key=notification_type.key,
        title=f"Aufgabe erledigt: {task.title}",
        body=f"Die Aufgabe '{task.title}' wurde als erledigt markiert.",
        metadata={
            "source": source,
            "event": "task_completed",
            "task_id": str(task.pk),
            "completed_by_id": str(actor.pk),
        },
        dedup_key_prefix=f"fetests.task.completed:{task.pk}",
        request_id=request_id,
        trace_id=trace_id,
    )
    return task
