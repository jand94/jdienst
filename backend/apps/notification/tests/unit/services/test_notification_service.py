import pytest

from apps.notification.api.v1.services.notification_service import (
    create_notification,
    mark_notifications_as_read_bulk,
)
from apps.notification.models import Notification, NotificationDelivery, NotificationType, UserNotificationPreference


@pytest.mark.django_db
def test_create_notification_creates_delivery_and_audit_event(user, tenant, monkeypatch):
    notification_type = NotificationType.objects.create(
        key="security-warning",
        title="Security Warning",
        default_channels=[UserNotificationPreference.CHANNEL_IN_APP, UserNotificationPreference.CHANNEL_REALTIME],
    )
    events = []
    monkeypatch.setattr(
        "apps.notification.api.v1.services.notification_service.record_audit_event",
        lambda **kwargs: events.append(kwargs),
    )

    notification = create_notification(
        tenant=tenant,
        actor=user,
        recipient=user,
        notification_type_key=notification_type.key,
        title="Warnung",
        body="Bitte Passwort rotieren.",
        metadata={"severity": "high"},
        dedup_key="sec-001",
        channels=None,
        request_id="req-123",
        trace_id="trace-abc",
    )

    deliveries = NotificationDelivery.objects.filter(notification=notification)
    assert notification.status == Notification.STATUS_UNREAD
    assert deliveries.count() == 2
    assert len(events) == 1
    assert events[0]["action"] == "notification.created"
    assert events[0]["metadata"]["source"] == "api"
    assert events[0]["metadata"]["classification"] == "security_notification_mutation"


@pytest.mark.django_db
def test_mark_notifications_as_read_bulk_updates_unread_records(user, tenant, monkeypatch):
    notification_type = NotificationType.objects.create(
        key="task-update",
        title="Task Update",
        default_channels=[UserNotificationPreference.CHANNEL_IN_APP],
    )
    first = Notification.objects.create(
        tenant=tenant,
        notification_type=notification_type,
        recipient=user,
        title="A",
        body="A body",
        status=Notification.STATUS_UNREAD,
    )
    second = Notification.objects.create(
        tenant=tenant,
        notification_type=notification_type,
        recipient=user,
        title="B",
        body="B body",
        status=Notification.STATUS_UNREAD,
    )
    events = []
    monkeypatch.setattr(
        "apps.notification.api.v1.services.notification_service.record_audit_event",
        lambda **kwargs: events.append(kwargs),
    )

    updated = mark_notifications_as_read_bulk(
        tenant=tenant,
        actor=user,
        notification_ids=[str(first.pk), str(second.pk)],
        request_id="req-789",
        trace_id="trace-789",
    )

    assert updated == 2
    assert Notification.objects.filter(status=Notification.STATUS_READ).count() == 2
    assert events[0]["action"] == "notification.bulk_read"
    assert events[0]["metadata"]["source"] == "api"
    assert events[0]["metadata"]["classification"] == "security_state_change"
