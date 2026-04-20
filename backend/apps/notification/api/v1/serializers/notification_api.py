from __future__ import annotations

from rest_framework import serializers

from apps.notification.models import Notification, NotificationType, UserNotificationPreference


class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = ("id", "key", "title", "description", "default_channels", "allow_user_opt_out", "is_active")
        read_only_fields = fields


class NotificationReadSerializer(serializers.ModelSerializer):
    notification_type = NotificationTypeSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "notification_type",
            "title",
            "body",
            "metadata",
            "status",
            "published_at",
            "read_at",
        )
        read_only_fields = fields


class NotificationCreateSerializer(serializers.Serializer):
    recipient_id = serializers.IntegerField(min_value=1)
    notification_type_key = serializers.SlugField(max_length=96)
    title = serializers.CharField(max_length=255)
    body = serializers.CharField()
    metadata = serializers.JSONField(required=False)
    dedup_key = serializers.CharField(required=False, allow_blank=True, max_length=255)
    channels = serializers.ListField(child=serializers.ChoiceField(choices=UserNotificationPreference.CHANNEL_CHOICES), required=False)


class NotificationBulkMarkReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)


class NotificationBulkArchiveSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)


class NotificationUnreadCountSerializer(serializers.Serializer):
    unread_count = serializers.IntegerField(min_value=0)


class NotificationPreferenceReadSerializer(serializers.ModelSerializer):
    notification_type = NotificationTypeSerializer(read_only=True)

    class Meta:
        model = UserNotificationPreference
        fields = ("id", "notification_type", "channel", "is_subscribed", "updated_at")
        read_only_fields = fields


class NotificationPreferenceUpdateSerializer(serializers.Serializer):
    notification_type_key = serializers.SlugField(max_length=96)
    channel = serializers.ChoiceField(choices=UserNotificationPreference.CHANNEL_CHOICES)
    is_subscribed = serializers.BooleanField()
