from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.common.api.v1.services import record_audit_event
from apps.common.models import Tenant
from apps.notification.api.v1.services.notification_preference_service import resolve_effective_channels
from apps.notification.models import Notification, NotificationDelivery, NotificationType

User = get_user_model()


def list_notifications_for_user(
    *,
    tenant: Tenant,
    user: User,
    include_archived: bool = False,
):
    queryset = Notification.objects.select_related("notification_type").filter(
        tenant=tenant,
        recipient=user,
    )
    if not include_archived:
        queryset = queryset.exclude(status=Notification.STATUS_ARCHIVED)
    return queryset.order_by("-published_at")


def create_notification(
    *,
    tenant: Tenant,
    actor: User,
    recipient: User,
    notification_type_key: str,
    title: str,
    body: str,
    metadata: dict | None,
    dedup_key: str,
    channels: list[str] | None,
    request_id: str | None,
    trace_id: str | None,
) -> Notification:
    notification_type = NotificationType.objects.get(key=notification_type_key, is_active=True)
    metadata_payload = dict(metadata or {})
    with transaction.atomic():
        notification = Notification.objects.create(
            tenant=tenant,
            notification_type=notification_type,
            recipient=recipient,
            actor=actor,
            title=title,
            body=body,
            metadata=metadata_payload,
            dedup_key=dedup_key.strip(),
            status=Notification.STATUS_UNREAD,
            published_at=timezone.now(),
        )
        effective_channels = resolve_effective_channels(
            user=recipient,
            notification_type=notification_type,
            requested_channels=channels,
        )
        deliveries = [
            NotificationDelivery(
                notification=notification,
                channel=channel,
                status=NotificationDelivery.STATUS_PENDING,
            )
            for channel in effective_channels
        ]
        if deliveries:
            NotificationDelivery.objects.bulk_create(deliveries)
        record_audit_event(
            action="notification.created",
            target_model="notification.Notification",
            target_id=str(notification.pk),
            actor=actor,
            metadata={
                "source": "api",
                "recipient_id": str(recipient.pk),
                "notification_type_key": notification_type.key,
                "channels": effective_channels,
            },
            request_id=request_id,
            trace_id=trace_id,
        )
    return notification


def mark_notification_as_read(
    *,
    tenant: Tenant,
    actor: User,
    notification: Notification,
    request_id: str | None,
    trace_id: str | None,
) -> Notification:
    if notification.tenant_id != tenant.pk or notification.recipient_id != actor.pk:
        raise Notification.DoesNotExist("Notification not found in tenant scope.")
    if notification.status == Notification.STATUS_READ:
        return notification
    notification.status = Notification.STATUS_READ
    notification.read_at = timezone.now()
    notification.save(update_fields=("status", "read_at", "updated_at"))
    record_audit_event(
        action="notification.read",
        target_model="notification.Notification",
        target_id=str(notification.pk),
        actor=actor,
        metadata={"source": "api"},
        request_id=request_id,
        trace_id=trace_id,
    )
    return notification


def mark_notifications_as_read_bulk(
    *,
    tenant: Tenant,
    actor: User,
    notification_ids: list[str],
    request_id: str | None,
    trace_id: str | None,
) -> int:
    notifications = Notification.objects.filter(
        pk__in=notification_ids,
        tenant=tenant,
        recipient=actor,
        status=Notification.STATUS_UNREAD,
    )
    affected_ids = list(notifications.values_list("id", flat=True))
    if not affected_ids:
        return 0
    now = timezone.now()
    notifications.update(status=Notification.STATUS_READ, read_at=now, updated_at=now)
    record_audit_event(
        action="notification.bulk_read",
        target_model="notification.Notification",
        target_id=str(actor.pk),
        actor=actor,
        metadata={"source": "api", "count": len(affected_ids)},
        request_id=request_id,
        trace_id=trace_id,
    )
    return len(affected_ids)
