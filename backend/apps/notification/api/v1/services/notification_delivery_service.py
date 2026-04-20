from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.common.api.v1.services import record_audit_event
from apps.notification.api.v1.services.notification_mail_service import NotificationMailDeliveryError, send_notification_email
from apps.notification.api.v1.services.notification_observability_service import log_pipeline_event
from apps.notification.api.v1.services.notification_realtime_service import publish_notification_realtime
from apps.notification.models import NotificationDelivery, UserNotificationPreference


def _max_attempts() -> int:
    value = getattr(settings, "NOTIFICATION_MAX_DELIVERY_ATTEMPTS", 5)
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 5


def _next_retry_time(*, attempt: int):
    base_seconds = getattr(settings, "NOTIFICATION_RETRY_BASE_SECONDS", 60)
    try:
        base_seconds = max(10, int(base_seconds))
    except (TypeError, ValueError):
        base_seconds = 60
    backoff_seconds = base_seconds * max(1, attempt)
    return timezone.now() + timedelta(seconds=backoff_seconds)


def _is_terminal_failure(*, attempt: int) -> bool:
    return attempt >= _max_attempts()


def _mark_delivery_failed(
    *,
    delivery: NotificationDelivery,
    reason: str,
    retryable: bool,
) -> None:
    if retryable and not _is_terminal_failure(attempt=delivery.attempts):
        delivery.status = NotificationDelivery.STATUS_PENDING
        delivery.last_error = reason
        delivery.next_attempt_at = _next_retry_time(attempt=delivery.attempts)
        return
    delivery.status = NotificationDelivery.STATUS_FAILED
    delivery.last_error = reason
    delivery.next_attempt_at = timezone.now()


def dispatch_delivery(*, delivery: NotificationDelivery) -> NotificationDelivery:
    notification = delivery.notification
    delivery.attempts += 1
    log_pipeline_event(
        event="notification.delivery.dispatch.start",
        delivery_id=str(delivery.pk),
        notification_id=str(notification.pk),
        channel=delivery.channel,
        attempts=delivery.attempts,
    )
    try:
        if delivery.channel == UserNotificationPreference.CHANNEL_IN_APP:
            delivery.status = NotificationDelivery.STATUS_SENT
            delivery.sent_at = timezone.now()
            delivery.last_error = ""
        elif delivery.channel == UserNotificationPreference.CHANNEL_REALTIME:
            publish_notification_realtime(notification=notification)
            delivery.status = NotificationDelivery.STATUS_SENT
            delivery.sent_at = timezone.now()
            delivery.last_error = ""
        elif delivery.channel == UserNotificationPreference.CHANNEL_EMAIL:
            send_notification_email(notification=notification)
            delivery.status = NotificationDelivery.STATUS_SENT
            delivery.sent_at = timezone.now()
            delivery.last_error = ""
        elif delivery.channel == UserNotificationPreference.CHANNEL_DIGEST:
            delivery.status = NotificationDelivery.STATUS_SKIPPED
            delivery.sent_at = timezone.now()
            delivery.last_error = "delivery_handled_by_digest_job"
        else:
            _mark_delivery_failed(
                delivery=delivery,
                reason="unsupported_channel",
                retryable=False,
            )
    except NotificationMailDeliveryError as exc:
        retryable = exc.reason in {"smtp_connect_error", "smtp_server_disconnected", "smtp_unexpected_error"}
        _mark_delivery_failed(
            delivery=delivery,
            reason=exc.reason,
            retryable=retryable,
        )
    except TimeoutError:
        _mark_delivery_failed(
            delivery=delivery,
            reason="delivery_timeout",
            retryable=True,
        )
    except Exception as exc:  # noqa: BLE001
        _mark_delivery_failed(
            delivery=delivery,
            reason=f"unexpected_error:{type(exc).__name__}",
            retryable=True,
        )
        log_pipeline_event(
            event="notification.delivery.dispatch.error",
            delivery_id=str(delivery.pk),
            notification_id=str(notification.pk),
            channel=delivery.channel,
            attempts=delivery.attempts,
            error=str(exc),
        )

    if delivery.status in {NotificationDelivery.STATUS_SENT, NotificationDelivery.STATUS_SKIPPED}:
        log_pipeline_event(
            event="notification.delivery.dispatch.complete",
            delivery_id=str(delivery.pk),
            notification_id=str(notification.pk),
            channel=delivery.channel,
            status=delivery.status,
            attempts=delivery.attempts,
        )
    else:
        log_pipeline_event(
            event="notification.delivery.dispatch.retry_or_failed",
            delivery_id=str(delivery.pk),
            notification_id=str(notification.pk),
            channel=delivery.channel,
            status=delivery.status,
            attempts=delivery.attempts,
            last_error=delivery.last_error,
            next_attempt_at=delivery.next_attempt_at.isoformat(),
        )

    delivery.save(
        update_fields=(
            "attempts",
            "status",
            "sent_at",
            "last_error",
            "next_attempt_at",
            "updated_at",
        )
    )
    record_audit_event(
        action="notification.delivery.status.updated",
        target_model="notification.NotificationDelivery",
        target_id=str(delivery.pk),
        actor=None,
        metadata={
            "source": "scheduler",
            "channel": delivery.channel,
            "status": delivery.status,
            "attempts": delivery.attempts,
            "last_error": delivery.last_error,
            "notification_id": str(notification.pk),
        },
    )
    return delivery


def dispatch_pending_deliveries(*, limit: int = 200) -> int:
    deliveries = (
        NotificationDelivery.objects.select_related("notification__recipient", "notification__notification_type")
        .filter(
            status=NotificationDelivery.STATUS_PENDING,
            next_attempt_at__lte=timezone.now(),
        )
        .order_by("next_attempt_at")[:limit]
    )
    dispatched = 0
    for delivery in deliveries:
        with transaction.atomic():
            dispatch_delivery(delivery=delivery)
        dispatched += 1
    return dispatched
