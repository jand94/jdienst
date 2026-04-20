from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.notification.api.v1.services.notification_delivery_service import dispatch_delivery
from apps.notification.api.v1.services.notification_mail_service import NotificationMailDeliveryError
from apps.notification.models import Notification, NotificationDelivery, NotificationType, UserNotificationPreference


@pytest.mark.django_db
def test_dispatch_delivery_marks_missing_email_as_terminal_failure(user, tenant):
    notification_type = NotificationType.objects.create(
        key="mail-terminal",
        title="Mail Terminal",
        default_channels=[UserNotificationPreference.CHANNEL_EMAIL],
    )
    user.email = ""
    user.save(update_fields=("email",))
    notification = Notification.objects.create(
        tenant=tenant,
        notification_type=notification_type,
        recipient=user,
        actor=user,
        title="Title",
        body="Body",
    )
    delivery = NotificationDelivery.objects.create(
        notification=notification,
        channel=UserNotificationPreference.CHANNEL_EMAIL,
        status=NotificationDelivery.STATUS_PENDING,
    )

    updated = dispatch_delivery(delivery=delivery)

    assert updated.status == NotificationDelivery.STATUS_FAILED
    assert updated.last_error == "recipient_missing_email"


@pytest.mark.django_db
def test_dispatch_delivery_retries_transient_mail_error_then_fails(user, tenant, monkeypatch, settings):
    settings.NOTIFICATION_MAX_DELIVERY_ATTEMPTS = 2
    notification_type = NotificationType.objects.create(
        key="mail-transient",
        title="Mail Transient",
        default_channels=[UserNotificationPreference.CHANNEL_EMAIL],
    )
    notification = Notification.objects.create(
        tenant=tenant,
        notification_type=notification_type,
        recipient=user,
        actor=user,
        title="Title",
        body="Body",
    )
    delivery = NotificationDelivery.objects.create(
        notification=notification,
        channel=UserNotificationPreference.CHANNEL_EMAIL,
        status=NotificationDelivery.STATUS_PENDING,
    )

    def _raise_transient(**kwargs):
        raise NotificationMailDeliveryError("smtp_connect_error", "temporary connect failure")

    monkeypatch.setattr(
        "apps.notification.api.v1.services.notification_delivery_service.send_notification_email",
        _raise_transient,
    )

    first = dispatch_delivery(delivery=delivery)
    first.refresh_from_db()
    assert first.status == NotificationDelivery.STATUS_PENDING
    assert first.last_error == "smtp_connect_error"
    assert first.next_attempt_at >= timezone.now() + timedelta(seconds=10)

    second = dispatch_delivery(delivery=first)
    assert second.status == NotificationDelivery.STATUS_FAILED
    assert second.attempts == 2
