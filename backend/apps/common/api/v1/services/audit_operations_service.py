from __future__ import annotations

from datetime import timedelta

from django.db.models import Count
from django.db.models import Q
from django.utils import timezone

from apps.common.models import AuditEvent

RETENTION_DAYS = {
    "security": 3650,
    "compliance": 2555,
    "operational": 365,
}


def classify_retention_class(action: str) -> str:
    if action.startswith(("auth.", "security.")):
        return "security"
    if action.startswith(("admin.", "common.audit_")):
        return "compliance"
    return "operational"


def archive_old_events(*, before_days: int) -> int:
    threshold = timezone.now() - timedelta(days=before_days)
    return (
        AuditEvent.objects.filter(created_at__lt=threshold, archived_at__isnull=True)
        .update(archived_at=timezone.now())
    )


def archive_events_by_retention_policy() -> int:
    now = timezone.now()
    archived_total = 0
    for retention_class, days in RETENTION_DAYS.items():
        threshold = now - timedelta(days=days)
        archived_total += (
            AuditEvent.objects.filter(
                created_at__lt=threshold,
                archived_at__isnull=True,
            )
            .filter(_retention_class_query(retention_class))
            .update(archived_at=now)
        )
    return archived_total


def _retention_class_query(retention_class: str) -> Q:
    if retention_class == "security":
        return Q(action__startswith="auth.") | Q(action__startswith="security.")
    if retention_class == "compliance":
        return Q(action__startswith="admin.") | Q(action__startswith="common.audit_")
    return ~(
        Q(action__startswith="auth.")
        | Q(action__startswith="security.")
        | Q(action__startswith="admin.")
        | Q(action__startswith="common.audit_")
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


def export_events_for_siem(*, limit: int = 500) -> tuple[list[dict], list[dict], list[str]]:
    payloads: list[dict] = []
    failures: list[dict] = []
    exported_ids: list[str] = []
    queryset = AuditEvent.objects.filter(exported_at__isnull=True).order_by("created_at")[:limit]
    for event in queryset:
        try:
            payload = build_siem_payload(event)
            payload["retention_class"] = classify_retention_class(event.action)
            payloads.append(payload)
            exported_ids.append(str(event.pk))
        except Exception as exc:  # pragma: no cover - defensive fallback
            failures.append(
                {
                    "event_id": str(event.pk),
                    "error": str(exc),
                }
            )
    return payloads, failures, exported_ids


def collect_audit_health_snapshot(*, window_hours: int = 24) -> dict:
    since = timezone.now() - timedelta(hours=window_hours)
    window_qs = AuditEvent.objects.filter(created_at__gte=since)
    aggregate_kwargs = {
        "events_total": Count("id"),
        "events_without_actor": Count("id", filter=Q(actor__isnull=True)),
        "events_not_exported": Count("id", filter=Q(exported_at__isnull=True)),
    }
    for retention_class in RETENTION_DAYS:
        aggregate_kwargs[f"retention_{retention_class}"] = Count(
            "id",
            filter=_retention_class_query(retention_class),
        )
    aggregate_counts = window_qs.aggregate(**aggregate_kwargs)
    volume_by_action = {
        row["action"]: row["total"]
        for row in window_qs.values("action").annotate(total=Count("id"))
    }
    return {
        "window_hours": window_hours,
        "events_total": aggregate_counts["events_total"],
        "events_without_actor": aggregate_counts["events_without_actor"],
        "events_not_exported": aggregate_counts["events_not_exported"],
        "retention_class_counts": {
            retention_class: aggregate_counts[f"retention_{retention_class}"]
            for retention_class in RETENTION_DAYS
        },
        "volume_by_action": volume_by_action,
    }
