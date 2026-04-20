from django.contrib import admin

from apps.notification.models import (
    Notification,
    NotificationDelivery,
    NotificationDigest,
    NotificationType,
    UserNotificationPreference,
)


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "is_active", "allow_user_opt_out", "updated_at")
    search_fields = ("key", "title")
    list_filter = ("is_active", "allow_user_opt_out")


@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "channel", "is_subscribed", "updated_at")
    search_fields = ("user__username", "user__email", "notification_type__key")
    list_filter = ("channel", "is_subscribed")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "notification_type", "status", "published_at", "read_at")
    search_fields = ("recipient__username", "recipient__email", "title", "notification_type__key")
    list_filter = ("status", "notification_type__key")
    readonly_fields = ("published_at", "read_at", "created_at", "updated_at")


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = ("notification", "channel", "status", "attempts", "next_attempt_at", "sent_at")
    list_filter = ("channel", "status")
    search_fields = ("notification__title", "notification__recipient__username")
    readonly_fields = ("created_at", "updated_at", "sent_at")


@admin.register(NotificationDigest)
class NotificationDigestAdmin(admin.ModelAdmin):
    list_display = ("recipient", "tenant", "status", "window_start", "window_end", "sent_at")
    list_filter = ("status",)
    search_fields = ("recipient__username", "recipient__email", "tenant__slug")
    readonly_fields = ("created_at", "updated_at", "sent_at")
