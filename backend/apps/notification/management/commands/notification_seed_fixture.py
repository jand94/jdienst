from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.common.models import Tenant, TenantMembership
from apps.notification.models import Notification, NotificationDelivery, NotificationType, UserNotificationPreference

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo notification types, preferences, notifications and delivery states."

    def add_arguments(self, parser):
        parser.add_argument("--tenant-slug", required=True, help="Tenant slug for seeded notification data.")
        parser.add_argument(
            "--user-email",
            required=True,
            help="Recipient email for seeded notifications and preferences.",
        )

    def handle(self, *args, **options):
        tenant_slug = options["tenant_slug"].strip()
        user_email = options["user_email"].strip().lower()
        tenant = Tenant.objects.filter(slug=tenant_slug).first()
        if tenant is None:
            raise CommandError(f"Tenant '{tenant_slug}' not found.")
        user = User.objects.filter(email=user_email).first()
        if user is None:
            raise CommandError(f"User with email '{user_email}' not found.")

        TenantMembership.objects.get_or_create(
            tenant=tenant,
            user=user,
            defaults={"role": TenantMembership.ROLE_MEMBER, "is_active": True},
        )

        type_specs = [
            {
                "key": "system-alert",
                "title": "System Alert",
                "description": "Operational alert for platform incidents.",
                "default_channels": [UserNotificationPreference.CHANNEL_IN_APP, UserNotificationPreference.CHANNEL_EMAIL],
            },
            {
                "key": "deployment-update",
                "title": "Deployment Update",
                "description": "Deployment and release updates.",
                "default_channels": [UserNotificationPreference.CHANNEL_IN_APP, UserNotificationPreference.CHANNEL_DIGEST],
            },
            {
                "key": "security-warning",
                "title": "Security Warning",
                "description": "Security-related notices with higher urgency.",
                "default_channels": [
                    UserNotificationPreference.CHANNEL_IN_APP,
                    UserNotificationPreference.CHANNEL_EMAIL,
                    UserNotificationPreference.CHANNEL_REALTIME,
                ],
            },
        ]

        notification_types: list[NotificationType] = []
        for spec in type_specs:
            notification_type, _ = NotificationType.objects.update_or_create(
                key=spec["key"],
                defaults={
                    "title": spec["title"],
                    "description": spec["description"],
                    "default_channels": spec["default_channels"],
                    "allow_user_opt_out": True,
                    "is_active": True,
                },
            )
            notification_types.append(notification_type)

        for notification_type in notification_types:
            UserNotificationPreference.objects.update_or_create(
                user=user,
                notification_type=notification_type,
                channel=UserNotificationPreference.CHANNEL_IN_APP,
                defaults={"is_subscribed": True},
            )
            UserNotificationPreference.objects.update_or_create(
                user=user,
                notification_type=notification_type,
                channel=UserNotificationPreference.CHANNEL_EMAIL,
                defaults={"is_subscribed": notification_type.key != "deployment-update"},
            )

        now = timezone.now()
        seeded = 0
        for index, notification_type in enumerate(notification_types, start=1):
            notification, created = Notification.objects.get_or_create(
                tenant=tenant,
                notification_type=notification_type,
                recipient=user,
                dedup_key=f"seed-{tenant.slug}-{notification_type.key}",
                defaults={
                    "actor": user,
                    "title": f"Seeded {notification_type.title}",
                    "body": f"Seed notification #{index} for diagnostics and UI demos.",
                    "metadata": {"source": "fixture_seed", "seed_index": index},
                    "status": Notification.STATUS_UNREAD,
                    "published_at": now,
                },
            )
            if created:
                seeded += 1
            NotificationDelivery.objects.update_or_create(
                notification=notification,
                channel=UserNotificationPreference.CHANNEL_IN_APP,
                defaults={"status": NotificationDelivery.STATUS_SENT, "attempts": 1, "sent_at": now, "last_error": ""},
            )
            NotificationDelivery.objects.update_or_create(
                notification=notification,
                channel=UserNotificationPreference.CHANNEL_EMAIL,
                defaults={
                    "status": NotificationDelivery.STATUS_FAILED if index == 2 else NotificationDelivery.STATUS_SENT,
                    "attempts": 2 if index == 2 else 1,
                    "sent_at": None if index == 2 else now,
                    "last_error": "smtp_connect_error" if index == 2 else "",
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"seeded_notification_types={len(notification_types)} "
                f"seeded_notifications_created={seeded} "
                f"tenant={tenant.slug} user={user.email}"
            )
        )
