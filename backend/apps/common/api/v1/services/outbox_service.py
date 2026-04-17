from __future__ import annotations

from datetime import timedelta
from typing import Any, Callable

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Count, Min, Q
from django.utils import timezone
from django.utils.module_loading import import_string

from apps.common.models import OutboxEvent

DEFAULT_OUTBOX_BATCH_SIZE = 100


def enqueue_outbox_event(
    *,
    topic: str,
    payload: dict[str, Any],
    headers: dict[str, Any] | None = None,
    dedup_key: str = "",
) -> OutboxEvent:
    if not topic.strip():
        raise ValueError("topic must not be empty")
    event = OutboxEvent(
        topic=topic,
        payload=payload,
        headers=headers or {},
        dedup_key=dedup_key,
        next_attempt_at=timezone.now(),
    )
    try:
        event.save()
    except IntegrityError:
        event = OutboxEvent.objects.filter(topic=topic, dedup_key=dedup_key).first()
        if event is None:
            raise
    return event


def _resolve_dispatch_handler() -> Callable[[OutboxEvent], None] | None:
    dotted_path = getattr(settings, "COMMON_OUTBOX_DISPATCH_HANDLER", "")
    if not dotted_path:
        return None
    return import_string(dotted_path)


def dispatch_pending_outbox_events(*, batch_size: int = DEFAULT_OUTBOX_BATCH_SIZE) -> dict[str, int]:
    now = timezone.now()
    handler = _resolve_dispatch_handler()
    success = 0
    failed = 0
    pending_qs = (
        OutboxEvent.objects.select_for_update(skip_locked=True)
        .filter(status=OutboxEvent.STATUS_PENDING, next_attempt_at__lte=now)
        .order_by("next_attempt_at", "created_at")[:batch_size]
    )
    with transaction.atomic():
        events = list(pending_qs)

    for event in events:
        try:
            if handler is not None:
                handler(event)
            event.status = OutboxEvent.STATUS_SENT
            event.sent_at = timezone.now()
            event.attempts += 1
            event.last_error = ""
            event.save(update_fields=("status", "sent_at", "attempts", "last_error", "updated_at"))
            success += 1
        except Exception as exc:  # pragma: no cover - defensive fallback
            event.status = OutboxEvent.STATUS_PENDING
            event.attempts += 1
            event.last_error = str(exc)
            event.next_attempt_at = timezone.now() + timedelta(seconds=min(300, 2**event.attempts))
            if event.attempts >= getattr(settings, "COMMON_OUTBOX_MAX_ATTEMPTS", 10):
                event.status = OutboxEvent.STATUS_FAILED
            event.save(update_fields=("status", "attempts", "last_error", "next_attempt_at", "updated_at"))
            failed += 1

    return {
        "processed": len(events),
        "sent": success,
        "failed": failed,
    }


def collect_outbox_health_snapshot() -> dict[str, Any]:
    now = timezone.now()
    aggregated = OutboxEvent.objects.aggregate(
        pending_total=Count("id", filter=Q(status=OutboxEvent.STATUS_PENDING)),
        failed_total=Count("id", filter=Q(status=OutboxEvent.STATUS_FAILED)),
        sent_total=Count("id", filter=Q(status=OutboxEvent.STATUS_SENT)),
        oldest_pending_at=Min(
            "created_at",
            filter=Q(status=OutboxEvent.STATUS_PENDING),
        ),
    )
    oldest_pending_at = aggregated["oldest_pending_at"]
    oldest_pending_age_seconds = 0
    if oldest_pending_at is not None:
        oldest_pending_age_seconds = int((now - oldest_pending_at).total_seconds())

    return {
        "pending_total": aggregated["pending_total"] or 0,
        "failed_total": aggregated["failed_total"] or 0,
        "sent_total": aggregated["sent_total"] or 0,
        "oldest_pending_age_seconds": oldest_pending_age_seconds,
    }
