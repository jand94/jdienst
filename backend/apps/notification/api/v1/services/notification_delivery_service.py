from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.notification.api.v1.services.notification_mail_service import send_notification_email
from apps.notification.api.v1.services.notification_realtime_service import publish_notification_realtime
from apps.notification.models import NotificationDelivery, UserNotificationPreference


def _next_retry_time(*, attempt: int):
    return timezone.now() + timedelta(minutes=max(1, attempt * 2))


def dispatch_delivery(*, delivery: NotificationDelivery) -> NotificationDelivery:
    notification = delivery.notification
    delivery.attempts += 1
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
            sent = send_notification_email(notification=notification)
            if sent:
                delivery.status = NotificationDelivery.STATUS_SENT
                delivery.sent_at = timezone.now()
                delivery.last_error = ""
            else:
                delivery.status = NotificationDelivery.STATUS_FAILED
                delivery.last_error = "recipient_has_no_email_or_delivery_failed"
                delivery.next_attempt_at = _next_retry_time(attempt=delivery.attempts)
        elif delivery.channel == UserNotificationPreference.CHANNEL_DIGEST:
            delivery.status = NotificationDelivery.STATUS_SKIPPED
            delivery.sent_at = timezone.now()
            delivery.last_error = "delivery_handled_by_digest_job"
        else:
            delivery.status = NotificationDelivery.STATUS_FAILED
            delivery.last_error = "unsupported_channel"
            delivery.next_attempt_at = _next_retry_time(attempt=delivery.attempts)
    except Exception as exc:  # noqa: BLE001
        delivery.status = NotificationDelivery.STATUS_FAILED
        delivery.last_error = str(exc)
        delivery.next_attempt_at = _next_retry_time(attempt=delivery.attempts)
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
