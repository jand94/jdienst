from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db.models import Count
from django.utils import timezone

from apps.notification.models import NotificationDelivery, NotificationDigest


def _env_int(name: str, default: int) -> int:
    value = getattr(settings, name, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def collect_notification_health_snapshot(*, window_hours: int = 24) -> dict:
    now = timezone.now()
    window_start = now - timedelta(hours=window_hours)
    max_attempts = _env_int("NOTIFICATION_MAX_DELIVERY_ATTEMPTS", 5)
    max_pending_total = _env_int("NOTIFICATION_HEALTH_MAX_PENDING_DELIVERIES", 1000)
    max_oldest_pending_age_seconds = _env_int("NOTIFICATION_HEALTH_MAX_OLDEST_PENDING_AGE_SECONDS", 900)

    pending_qs = NotificationDelivery.objects.filter(status=NotificationDelivery.STATUS_PENDING)
    pending_total = pending_qs.count()
    oldest_pending = pending_qs.order_by("next_attempt_at").values_list("next_attempt_at", flat=True).first()
    if oldest_pending is None:
        oldest_pending_age_seconds = 0
    else:
        oldest_pending_age_seconds = max(0, int((now - oldest_pending).total_seconds()))

    failed_qs = NotificationDelivery.objects.filter(status=NotificationDelivery.STATUS_FAILED)
    failed_total = failed_qs.count()
    terminal_failed_total = failed_qs.filter(attempts__gte=max_attempts).count()
    retryable_failed_total = failed_qs.filter(attempts__lt=max_attempts).count()
    retries_due_total = pending_qs.filter(next_attempt_at__lte=now).count()

    digest_pending_total = NotificationDigest.objects.filter(status=NotificationDigest.STATUS_PENDING).count()
    digest_failed_total = NotificationDigest.objects.filter(status=NotificationDigest.STATUS_FAILED).count()

    recent_delivery_counts = NotificationDelivery.objects.filter(created_at__gte=window_start).values("status").annotate(
        total=Count("id")
    )
    status_totals = {item["status"]: item["total"] for item in recent_delivery_counts}
    success_total = int(status_totals.get(NotificationDelivery.STATUS_SENT, 0))
    skipped_total = int(status_totals.get(NotificationDelivery.STATUS_SKIPPED, 0))
    recent_failed_total = int(status_totals.get(NotificationDelivery.STATUS_FAILED, 0))
    denominator = success_total + skipped_total + recent_failed_total
    success_rate = 1.0 if denominator == 0 else round(success_total / denominator, 4)

    checks = {
        "pending_within_limit": pending_total <= max_pending_total,
        "oldest_pending_within_limit": oldest_pending_age_seconds <= max_oldest_pending_age_seconds,
    }
    passed = all(checks.values())

    return {
        "window_hours": window_hours,
        "passed": passed,
        "checks": checks,
        "delivery": {
            "pending_total": pending_total,
            "failed_total": failed_total,
            "terminal_failed_total": terminal_failed_total,
            "retryable_failed_total": retryable_failed_total,
            "retries_due_total": retries_due_total,
            "oldest_pending_age_seconds": oldest_pending_age_seconds,
            "recent_success_rate": success_rate,
            "recent_sent_total": success_total,
            "recent_failed_total": recent_failed_total,
            "recent_skipped_total": skipped_total,
            "max_attempts": max_attempts,
        },
        "digest": {
            "pending_total": digest_pending_total,
            "failed_total": digest_failed_total,
        },
        "thresholds": {
            "max_pending_total": max_pending_total,
            "max_oldest_pending_age_seconds": max_oldest_pending_age_seconds,
        },
    }
