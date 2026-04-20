from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.notification.models import Notification


def notification_group_name(*, user_id) -> str:
    return f"notifications.user.{user_id}"


def publish_notification_realtime(*, notification: Notification) -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    payload = {
        "type": "notification.message",
        "event": "notification.created",
        "data": {
            "id": str(notification.pk),
            "title": notification.title,
            "body": notification.body,
            "status": notification.status,
            "published_at": notification.published_at.isoformat(),
            "notification_type_key": notification.notification_type.key,
        },
    }
    async_to_sync(channel_layer.group_send)(
        notification_group_name(user_id=notification.recipient_id),
        payload,
    )
