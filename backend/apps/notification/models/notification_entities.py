from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import Tenant, TimeStampedModel, UUIDPrimaryKeyModel


class NotificationType(UUIDPrimaryKeyModel, TimeStampedModel):
    key = models.SlugField(max_length=96, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    default_channels = models.JSONField(default=list, blank=True)
    allow_user_opt_out = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=("is_active", "key"), name="notif_type_active_key_idx"),
        ]

    def __str__(self) -> str:
        return self.key


class Notification(UUIDPrimaryKeyModel, TimeStampedModel):
    STATUS_UNREAD = "unread"
    STATUS_READ = "read"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = (
        (STATUS_UNREAD, "Unread"),
        (STATUS_READ, "Read"),
        (STATUS_ARCHIVED, "Archived"),
    )

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.PROTECT,
        related_name="notifications",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications_received",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications_triggered",
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_UNREAD,
        db_index=True,
    )
    dedup_key = models.CharField(max_length=255, blank=True, default="")
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=("recipient", "status", "-published_at"), name="notif_rcpt_status_pub_idx"),
            models.Index(fields=("tenant", "recipient", "-published_at"), name="notif_tenant_rcpt_pub_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("recipient", "notification_type", "dedup_key"),
                condition=~models.Q(dedup_key=""),
                name="notif_rcpt_type_dedup_unique",
            )
        ]

    def __str__(self) -> str:
        return f"{self.recipient_id}:{self.notification_type.key}:{self.status}"


class UserNotificationPreference(UUIDPrimaryKeyModel, TimeStampedModel):
    CHANNEL_IN_APP = "in_app"
    CHANNEL_EMAIL = "email"
    CHANNEL_REALTIME = "realtime"
    CHANNEL_DIGEST = "digest"
    CHANNEL_CHOICES = (
        (CHANNEL_IN_APP, "In-App"),
        (CHANNEL_EMAIL, "Email"),
        (CHANNEL_REALTIME, "Realtime"),
        (CHANNEL_DIGEST, "Digest"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.CASCADE,
        related_name="user_preferences",
    )
    channel = models.CharField(max_length=32, choices=CHANNEL_CHOICES)
    is_subscribed = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "notification_type", "channel"),
                name="notif_pref_user_type_channel_unique",
            )
        ]
        indexes = [
            models.Index(fields=("user", "channel"), name="notif_pref_user_channel_idx"),
            models.Index(fields=("notification_type", "channel"), name="notif_pref_type_channel_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.notification_type.key}:{self.channel}"


class NotificationDelivery(UUIDPrimaryKeyModel, TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_SKIPPED = "skipped"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
        (STATUS_SKIPPED, "Skipped"),
    )

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    channel = models.CharField(max_length=32, choices=UserNotificationPreference.CHANNEL_CHOICES)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    attempts = models.PositiveIntegerField(default=0)
    sent_at = models.DateTimeField(null=True, blank=True, db_index=True)
    next_attempt_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_error = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("notification", "channel"),
                name="notif_delivery_notification_channel_unique",
            )
        ]
        indexes = [
            models.Index(fields=("status", "next_attempt_at"), name="notif_deliv_status_retry_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.notification_id}:{self.channel}:{self.status}"


class NotificationDigest(UUIDPrimaryKeyModel, TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    )

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="notification_digests")
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_digests",
    )
    window_start = models.DateTimeField(db_index=True)
    window_end = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    notifications = models.ManyToManyField(Notification, related_name="digests", blank=True)
    attempts = models.PositiveIntegerField(default=0)
    sent_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_error = models.TextField(blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=("recipient", "status", "-window_end"), name="notif_digest_user_status_idx"),
            models.Index(fields=("tenant", "status", "-window_end"), name="notif_digest_tenant_status_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("recipient", "window_start", "window_end"),
                name="notif_digest_user_window_unique",
            )
        ]

    def __str__(self) -> str:
        return f"{self.recipient_id}:{self.window_start.isoformat()}-{self.window_end.isoformat()}"
