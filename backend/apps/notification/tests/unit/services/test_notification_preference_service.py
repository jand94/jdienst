import pytest

from apps.notification.api.v1.services.notification_preference_service import (
    resolve_channel_subscription,
    resolve_effective_channels,
    set_user_preference,
)
from apps.notification.models import NotificationType, UserNotificationPreference


@pytest.mark.django_db
def test_resolve_channel_subscription_uses_default_channels(user):
    notification_type = NotificationType.objects.create(
        key="incident-alert",
        title="Incident Alert",
        default_channels=[
            UserNotificationPreference.CHANNEL_IN_APP,
            UserNotificationPreference.CHANNEL_EMAIL,
        ],
        allow_user_opt_out=True,
    )

    assert (
        resolve_channel_subscription(
            user=user,
            notification_type=notification_type,
            channel=UserNotificationPreference.CHANNEL_EMAIL,
        )
        is True
    )


@pytest.mark.django_db
def test_set_user_preference_overrides_default_subscription(user, monkeypatch):
    notification_type = NotificationType.objects.create(
        key="daily-summary",
        title="Daily Summary",
        default_channels=[UserNotificationPreference.CHANNEL_EMAIL],
        allow_user_opt_out=True,
    )

    events = []
    monkeypatch.setattr(
        "apps.notification.api.v1.services.notification_preference_service.record_audit_event",
        lambda **kwargs: events.append(kwargs),
    )
    set_user_preference(
        user=user,
        notification_type=notification_type,
        channel=UserNotificationPreference.CHANNEL_EMAIL,
        is_subscribed=False,
        request_id="req-pref",
        trace_id="trace-pref",
    )

    assert (
        resolve_channel_subscription(
            user=user,
            notification_type=notification_type,
            channel=UserNotificationPreference.CHANNEL_EMAIL,
        )
        is False
    )
    assert events[0]["action"] == "notification.preference.updated"
    assert events[0]["metadata"]["source"] == "api"


@pytest.mark.django_db
def test_resolve_effective_channels_filters_unsubscribed(user):
    notification_type = NotificationType.objects.create(
        key="ops-event",
        title="Ops Event",
        default_channels=[
            UserNotificationPreference.CHANNEL_IN_APP,
            UserNotificationPreference.CHANNEL_EMAIL,
            UserNotificationPreference.CHANNEL_REALTIME,
        ],
        allow_user_opt_out=True,
    )
    set_user_preference(
        user=user,
        notification_type=notification_type,
        channel=UserNotificationPreference.CHANNEL_EMAIL,
        is_subscribed=False,
    )

    channels = resolve_effective_channels(
        user=user,
        notification_type=notification_type,
        requested_channels=None,
    )

    assert UserNotificationPreference.CHANNEL_EMAIL not in channels
    assert UserNotificationPreference.CHANNEL_IN_APP in channels
