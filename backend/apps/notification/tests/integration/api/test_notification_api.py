import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.notification.models import Notification, NotificationType, UserNotificationPreference

User = get_user_model()


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
def test_notification_create_returns_mapped_error_for_non_member_recipient(
    api_client,
    staff_user,
    tenant,
    staff_tenant_membership,
):
    external_user = User.objects.create_user(
        email="external-notification@example.com",
        username="external_notification",
        password="pw123456!",
    )
    NotificationType.objects.create(
        key="quota-warning-external",
        title="Quota Warning External",
        default_channels=[UserNotificationPreference.CHANNEL_IN_APP],
    )
    api_client.force_authenticate(user=staff_user)

    response = api_client.post(
        "/api/notification/v1/notifications/",
        {
            "recipient_id": str(external_user.pk),
            "notification_type_key": "quota-warning-external",
            "title": "Quota",
            "body": "Bitte aufraeumen.",
            "channels": [UserNotificationPreference.CHANNEL_IN_APP],
        },
        format="json",
        HTTP_X_TENANT_SLUG=tenant.slug,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data
    assert response.data["error"]["code"] == "invalid"


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


@pytest.mark.django_db
def test_staff_can_read_notification_health_snapshot(api_client, staff_user, tenant, staff_tenant_membership):
    api_client.force_authenticate(user=staff_user)

    response = api_client.get(
        "/api/notification/v1/ops/health-snapshot/",
        HTTP_X_TENANT_SLUG=tenant.slug,
    )

    assert response.status_code == status.HTTP_200_OK
    assert "delivery" in response.data
    assert "digest" in response.data


@pytest.mark.django_db
def test_non_staff_cannot_read_notification_health_snapshot(api_client, user, tenant, tenant_membership):
    api_client.force_authenticate(user=user)

    response = api_client.get(
        "/api/notification/v1/ops/health-snapshot/",
        HTTP_X_TENANT_SLUG=tenant.slug,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_notification_create_is_throttled(
    api_client,
    staff_user,
    user,
    tenant,
    staff_tenant_membership,
    tenant_membership,
    settings,
):
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["notification_create"] = "1/minute"
    NotificationType.objects.create(
        key="throttle-create",
        title="Throttle Create",
        default_channels=[UserNotificationPreference.CHANNEL_IN_APP],
    )
    api_client.force_authenticate(user=staff_user)
    payload = {
        "recipient_id": str(user.pk),
        "notification_type_key": "throttle-create",
        "title": "A",
        "body": "A",
        "channels": [UserNotificationPreference.CHANNEL_IN_APP],
    }

    first = api_client.post("/api/notification/v1/notifications/", payload, format="json", HTTP_X_TENANT_SLUG=tenant.slug)
    second = api_client.post("/api/notification/v1/notifications/", payload, format="json", HTTP_X_TENANT_SLUG=tenant.slug)

    assert first.status_code == status.HTTP_201_CREATED
    assert second.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
def test_notification_preference_update_is_throttled(api_client, user, tenant, tenant_membership, settings):
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["notification_preference_update"] = "1/minute"
    NotificationType.objects.create(
        key="throttle-preference",
        title="Throttle Preference",
        default_channels=[UserNotificationPreference.CHANNEL_DIGEST],
    )
    api_client.force_authenticate(user=user)
    payload = {
        "notification_type_key": "throttle-preference",
        "channel": UserNotificationPreference.CHANNEL_DIGEST,
        "is_subscribed": False,
    }

    first = api_client.post("/api/notification/v1/preferences/", payload, format="json", HTTP_X_TENANT_SLUG=tenant.slug)
    second = api_client.post("/api/notification/v1/preferences/", payload, format="json", HTTP_X_TENANT_SLUG=tenant.slug)

    assert first.status_code == status.HTTP_201_CREATED
    assert second.status_code == status.HTTP_429_TOO_MANY_REQUESTS
