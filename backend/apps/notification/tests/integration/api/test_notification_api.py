import pytest
from rest_framework import status

from apps.notification.models import Notification, NotificationType, UserNotificationPreference


@pytest.mark.django_db
def test_notification_list_returns_user_notifications(api_client, user, tenant, tenant_membership):
    notification_type = NotificationType.objects.create(
        key="build-failed",
        title="Build Failed",
        default_channels=[UserNotificationPreference.CHANNEL_IN_APP],
    )
    Notification.objects.create(
        tenant=tenant,
        notification_type=notification_type,
        recipient=user,
        title="Pipeline Fehler",
        body="Build #42 ist fehlgeschlagen.",
    )
    api_client.force_authenticate(user=user)

    response = api_client.get(
        "/api/notification/v1/notifications/",
        HTTP_X_TENANT_SLUG=tenant.slug,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Pipeline Fehler"


@pytest.mark.django_db
def test_staff_can_create_notification(api_client, staff_user, user, tenant, staff_tenant_membership, tenant_membership):
    NotificationType.objects.create(
        key="quota-warning",
        title="Quota Warning",
        default_channels=[UserNotificationPreference.CHANNEL_IN_APP, UserNotificationPreference.CHANNEL_EMAIL],
    )
    api_client.force_authenticate(user=staff_user)

    response = api_client.post(
        "/api/notification/v1/notifications/",
        {
            "recipient_id": str(user.pk),
            "notification_type_key": "quota-warning",
            "title": "Quota",
            "body": "Bitte aufraeumen.",
            "channels": [UserNotificationPreference.CHANNEL_IN_APP],
        },
        format="json",
        HTTP_X_TENANT_SLUG=tenant.slug,
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Notification.objects.filter(recipient=user, tenant=tenant).count() == 1


@pytest.mark.django_db
def test_user_can_mark_notification_as_read(api_client, user, tenant, tenant_membership):
    notification_type = NotificationType.objects.create(
        key="release-ready",
        title="Release Ready",
        default_channels=[UserNotificationPreference.CHANNEL_IN_APP],
    )
    notification = Notification.objects.create(
        tenant=tenant,
        notification_type=notification_type,
        recipient=user,
        title="Release",
        body="Deploy kann gestartet werden.",
        status=Notification.STATUS_UNREAD,
    )
    api_client.force_authenticate(user=user)

    response = api_client.post(
        f"/api/notification/v1/notifications/{notification.pk}/mark-read/",
        HTTP_X_TENANT_SLUG=tenant.slug,
    )

    assert response.status_code == status.HTTP_200_OK
    notification.refresh_from_db()
    assert notification.status == Notification.STATUS_READ


@pytest.mark.django_db
def test_user_can_subscribe_or_unsubscribe_preference(api_client, user, tenant, tenant_membership):
    NotificationType.objects.create(
        key="digest-only",
        title="Digest Only",
        default_channels=[UserNotificationPreference.CHANNEL_DIGEST],
    )
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/notification/v1/preferences/",
        {
            "notification_type_key": "digest-only",
            "channel": UserNotificationPreference.CHANNEL_DIGEST,
            "is_subscribed": False,
        },
        format="json",
        HTTP_X_TENANT_SLUG=tenant.slug,
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["is_subscribed"] is False
