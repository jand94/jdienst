import pytest

from apps.notification.models import Notification, NotificationDelivery, NotificationType, UserNotificationPreference
from apps.notification.tasks.notification_tasks import (
    run_notification_delivery_dispatch,
    run_notification_digest_build,
    run_notification_digest_dispatch,
)


@pytest.mark.django_db
def test_delivery_task_dispatches_pending_in_app_delivery(user, tenant):
    notification_type = NotificationType.objects.create(
        key="infra-event",
        title="Infra Event",
        default_channels=[UserNotificationPreference.CHANNEL_IN_APP],
    )
    notification = Notification.objects.create(
        tenant=tenant,
        notification_type=notification_type,
        recipient=user,
        title="Node restarted",
        body="node-1 wurde neu gestartet",
    )
    NotificationDelivery.objects.create(
        notification=notification,
        channel=UserNotificationPreference.CHANNEL_IN_APP,
        status=NotificationDelivery.STATUS_PENDING,
    )

    processed = run_notification_delivery_dispatch()

    assert processed == 1
    assert NotificationDelivery.objects.get(notification=notification).status == NotificationDelivery.STATUS_SENT


@pytest.mark.django_db
def test_digest_tasks_run_without_errors(user, tenant):
    notification_type = NotificationType.objects.create(
        key="digest-task",
        title="Digest Task",
        default_channels=[UserNotificationPreference.CHANNEL_DIGEST],
    )
    Notification.objects.create(
        tenant=tenant,
        notification_type=notification_type,
        recipient=user,
        title="Task A",
        body="A",
    )

    build_count = run_notification_digest_build()
    dispatch_count = run_notification_digest_dispatch()

    assert build_count >= 0
    assert dispatch_count >= 0
