from __future__ import annotations

import pytest

from apps.notification.api.v1.services.notification_health_service import collect_notification_health_snapshot
from apps.notification.models import Notification, NotificationDelivery, NotificationDigest, NotificationType, UserNotificationPreference


@pytest.mark.django_db
def test_collect_notification_health_snapshot_returns_delivery_and_digest_metrics(user, tenant):
    notification_type = NotificationType.objects.create(
        key="health-service",
        title="Health Service",
        default_channels=[UserNotificationPreference.CHANNEL_IN_APP],
    )
    notification = Notification.objects.create(
        tenant=tenant,
        notification_type=notification_type,
        recipient=user,
        title="A",
        body="A",
    )
    NotificationDelivery.objects.create(
        notification=notification,
        channel=UserNotificationPreference.CHANNEL_IN_APP,
        status=NotificationDelivery.STATUS_PENDING,
    )
    NotificationDigest.objects.create(
        tenant=tenant,
        recipient=user,
        window_start=notification.published_at,
        window_end=notification.published_at,
        status=NotificationDigest.STATUS_FAILED,
    )

    snapshot = collect_notification_health_snapshot(window_hours=24)

    assert "delivery" in snapshot
    assert "digest" in snapshot
    assert snapshot["delivery"]["pending_total"] >= 1
    assert snapshot["digest"]["failed_total"] >= 1
