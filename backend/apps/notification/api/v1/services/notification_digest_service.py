from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.common.api.v1.services import record_audit_event
from apps.notification.api.v1.services.notification_mail_service import send_digest_email
from apps.notification.models import Notification, NotificationDigest, UserNotificationPreference


def _digest_window_minutes() -> int:
    return max(5, int(getattr(settings, "NOTIFICATION_DIGEST_WINDOW_MINUTES", 60)))


def build_pending_digests(*, now=None) -> int:
    current_time = now or timezone.now()
    window_end = current_time
    window_start = current_time - timedelta(minutes=_digest_window_minutes())

    recipients = (
        Notification.objects.filter(
            status=Notification.STATUS_UNREAD,
            published_at__gte=window_start,
            published_at__lte=window_end,
        )
        .values_list("tenant_id", "recipient_id")
        .distinct()
    )

    created = 0
    for tenant_id, recipient_id in recipients:
        digest, digest_created = NotificationDigest.objects.get_or_create(
            tenant_id=tenant_id,
            recipient_id=recipient_id,
            window_start=window_start,
            window_end=window_end,
            defaults={"status": NotificationDigest.STATUS_PENDING},
        )
        if not digest_created:
            continue
        digest_notifications = Notification.objects.filter(
            tenant_id=tenant_id,
            recipient_id=recipient_id,
            status=Notification.STATUS_UNREAD,
            published_at__gte=window_start,
            published_at__lte=window_end,
        ).exclude(
            notification_type__user_preferences__user_id=recipient_id,
            notification_type__user_preferences__channel=UserNotificationPreference.CHANNEL_DIGEST,
            notification_type__user_preferences__is_subscribed=False,
        )
        digest.notifications.set(digest_notifications)
        created += 1
    return created


def dispatch_pending_digests(*, limit: int = 50) -> int:
    digests = (
        NotificationDigest.objects.select_related("recipient")
        .prefetch_related("notifications__notification_type")
        .filter(status=NotificationDigest.STATUS_PENDING)
        .order_by("window_end")[:limit]
    )
    processed = 0
    for digest in digests:
        notifications = list(digest.notifications.all())
        if not notifications:
            digest.status = NotificationDigest.STATUS_SENT
            digest.sent_at = timezone.now()
            digest.save(update_fields=("status", "sent_at", "updated_at"))
            continue
        try:
            subject = f"{len(notifications)} neue Benachrichtigungen"
            lines = [f"- {item.title}" for item in notifications]
            body = "\n".join(lines)
            sent_count = send_digest_email(
                recipient_email=digest.recipient.email,
                subject=subject,
                body=body,
            )
            with transaction.atomic():
                digest.attempts += 1
                digest.status = NotificationDigest.STATUS_SENT if sent_count else NotificationDigest.STATUS_FAILED
                digest.sent_at = timezone.now() if sent_count else None
                digest.last_error = "" if sent_count else "recipient_has_no_email_or_delivery_failed"
                digest.save(update_fields=("attempts", "status", "sent_at", "last_error", "updated_at"))
                record_audit_event(
                    action="notification.digest.dispatched",
                    target_model="notification.NotificationDigest",
                    target_id=str(digest.pk),
                    actor=None,
                    metadata={"source": "scheduler", "notifications": len(notifications), "sent_count": sent_count},
                )
        except Exception as exc:  # noqa: BLE001
            digest.attempts += 1
            digest.status = NotificationDigest.STATUS_FAILED
            digest.last_error = str(exc)
            digest.save(update_fields=("attempts", "status", "last_error", "updated_at"))
        processed += 1
    return processed
