import pytest

from apps.notification.api.v1.services.notification_service import (
    archive_notification,
    archive_notifications_bulk,
    create_notification,
    mark_notifications_as_read_bulk,
    unread_notification_count,
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


@pytest.mark.django_db
def test_archive_notification_sets_status_and_writes_audit(user, tenant, monkeypatch):
    notification_type = NotificationType.objects.create(
        key="archive-item",
        title="Archive Item",
        default_channels=[UserNotificationPreference.CHANNEL_IN_APP],
    )
    notification = Notification.objects.create(
        tenant=tenant,
        notification_type=notification_type,
        recipient=user,
        title="Archivierbar",
        body="Body",
        status=Notification.STATUS_UNREAD,
    )
    events = []
    monkeypatch.setattr(
        "apps.notification.api.v1.services.notification_service.record_audit_event",
        lambda **kwargs: events.append(kwargs),
    )

    updated = archive_notification(
        tenant=tenant,
        actor=user,
        notification=notification,
        request_id="req-archive",
        trace_id="trace-archive",
    )

    assert updated.status == Notification.STATUS_ARCHIVED
    assert updated.read_at is not None
    assert events[0]["action"] == "notification.archived"
    assert events[0]["metadata"]["classification"] == "security_state_change"


@pytest.mark.django_db
def test_archive_notifications_bulk_and_unread_count(user, tenant, monkeypatch):
    notification_type = NotificationType.objects.create(
        key="archive-bulk",
        title="Archive Bulk",
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

    updated = archive_notifications_bulk(
        tenant=tenant,
        actor=user,
        notification_ids=[str(first.pk), str(second.pk)],
        request_id="req-bulk-archive",
        trace_id="trace-bulk-archive",
    )

    assert updated == 2
    assert Notification.objects.filter(status=Notification.STATUS_ARCHIVED).count() == 2
    assert unread_notification_count(tenant=tenant, user=user) == 0
    assert events[0]["action"] == "notification.bulk_archived"
