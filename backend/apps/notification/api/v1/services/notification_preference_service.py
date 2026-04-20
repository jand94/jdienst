from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.common.api.v1.services import record_audit_event
from apps.notification.models import NotificationType, UserNotificationPreference

User = get_user_model()


def list_user_preferences(*, user: User):
    return UserNotificationPreference.objects.select_related("notification_type").filter(user=user).order_by(
        "notification_type__key",
        "channel",
    )


def set_user_preference(
    *,
    user: User,
    notification_type: NotificationType,
    channel: str,
    is_subscribed: bool,
    request_id: str | None = None,
    trace_id: str | None = None,
) -> UserNotificationPreference:
    preference, _ = UserNotificationPreference.objects.update_or_create(
        user=user,
        notification_type=notification_type,
        channel=channel,
        defaults={"is_subscribed": is_subscribed},
    )
    record_audit_event(
        action="notification.preference.updated",
        target_model="notification.UserNotificationPreference",
        target_id=str(preference.pk),
        actor=user,
        metadata={
            "source": "api",
            "notification_type_key": notification_type.key,
            "channel": channel,
            "is_subscribed": is_subscribed,
        },
        request_id=request_id,
        trace_id=trace_id,
    )
    return preference


def resolve_channel_subscription(
    *,
    user: User,
    notification_type: NotificationType,
    channel: str,
) -> bool:
    preference = UserNotificationPreference.objects.filter(
        user=user,
        notification_type=notification_type,
        channel=channel,
    ).first()
    if preference is not None:
        return preference.is_subscribed
    if not notification_type.allow_user_opt_out:
        return True
    return channel in list(notification_type.default_channels)


def resolve_effective_channels(
    *,
    user: User,
    notification_type: NotificationType,
    requested_channels: list[str] | None,
) -> list[str]:
    channels = requested_channels if requested_channels else list(notification_type.default_channels)
    resolved: list[str] = []
    for channel in channels:
        if resolve_channel_subscription(
            user=user,
            notification_type=notification_type,
            channel=channel,
        ):
            resolved.append(channel)
    return list(dict.fromkeys(resolved))
