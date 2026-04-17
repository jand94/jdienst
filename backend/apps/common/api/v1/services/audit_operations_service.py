from __future__ import annotations

from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from apps.common.models import AuditEvent


def archive_old_events(*, before_days: int) -> int:
    threshold = timezone.now() - timedelta(days=before_days)
    return (
        AuditEvent.objects.filter(created_at__lt=threshold, archived_at__isnull=True)
        .update(archived_at=timezone.now())
    )


def build_siem_payload(event: AuditEvent) -> dict:
    return {
        "id": str(event.pk),
        "created_at": event.created_at.isoformat(),
        "action": event.action,
        "target_model": event.target_model,
        "target_id": event.target_id,
        "actor_id": event.actor_id,
        "metadata": event.metadata,
        "ip_address": event.ip_address,
        "user_agent": event.user_agent,
        "integrity_hash": event.integrity_hash,
        "previous_hash": event.previous_hash,
    }


def mark_events_exported(*, event_ids: list[str]) -> int:
    if not event_ids:
        return 0
    return AuditEvent.objects.filter(pk__in=event_ids).update(exported_at=timezone.now())


def collect_audit_health_snapshot(*, window_hours: int = 24) -> dict:
    since = timezone.now() - timedelta(hours=window_hours)
    window_qs = AuditEvent.objects.filter(created_at__gte=since)
    volume_by_action = {
        row["action"]: row["total"]
        for row in window_qs.values("action").annotate(total=Count("id"))
    }
    return {
        "window_hours": window_hours,
        "events_total": window_qs.count(),
        "events_without_actor": window_qs.filter(actor__isnull=True).count(),
        "events_not_exported": window_qs.filter(exported_at__isnull=True).count(),
        "volume_by_action": volume_by_action,
    }
