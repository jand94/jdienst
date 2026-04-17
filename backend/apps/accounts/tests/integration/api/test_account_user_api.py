import pytest
from django.urls import reverse

from apps.common.models import AuditEvent
from apps.common.tests.factories import UserFactory


@pytest.mark.django_db
def test_list_users_requires_staff_permission(api_client):
    user = UserFactory(is_staff=False)
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("accounts-user-list"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_list_users_returns_paginated_results_for_staff(api_client):
    staff_user = UserFactory(is_staff=True)
    UserFactory.create_batch(3)
    api_client.force_authenticate(user=staff_user)

    response = api_client.get(reverse("accounts-user-list"))

    assert response.status_code == 200
    assert "results" in response.data
    assert response.data["count"] >= 4
    assert AuditEvent.objects.filter(
        action="accounts.user.listed",
        target_model="accounts.User",
        target_id=str(staff_user.pk),
    ).exists()


@pytest.mark.django_db
def test_me_endpoint_returns_authenticated_user(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("accounts-user-me"))

    assert response.status_code == 200
    assert response.data["id"] == user.id
    assert response.data["username"] == user.username
    assert AuditEvent.objects.filter(
        action="accounts.user.read",
        target_model="accounts.User",
        target_id=str(user.pk),
        metadata__scope="self",
    ).exists()


@pytest.mark.django_db
def test_patch_me_updates_profile_and_creates_audit_event(api_client):
    user = UserFactory(first_name="Old")
    api_client.force_authenticate(user=user)

    response = api_client.patch(
        reverse("accounts-user-me"),
        data={"first_name": "New"},
        format="json",
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == "New"
    event = AuditEvent.objects.filter(
        action="accounts.user.updated",
        target_model="accounts.User",
        target_id=str(user.pk),
    ).first()
    assert event is not None


@pytest.mark.django_db
def test_retrieve_foreign_user_is_forbidden_and_audited(api_client):
    actor = UserFactory()
    other_user = UserFactory()
    api_client.force_authenticate(user=actor)

    response = api_client.get(reverse("accounts-user-detail", kwargs={"pk": other_user.pk}))

    assert response.status_code == 403
    denied_event = AuditEvent.objects.filter(
        action="security.permission.denied",
        target_model="accounts.User",
        target_id=str(actor.pk),
    ).first()
    assert denied_event is not None


@pytest.mark.django_db
def test_retrieve_user_logs_read_access_for_staff(api_client):
    staff = UserFactory(is_staff=True)
    target_user = UserFactory()
    api_client.force_authenticate(user=staff)

    response = api_client.get(reverse("accounts-user-detail", kwargs={"pk": target_user.pk}))

    assert response.status_code == 200
    assert AuditEvent.objects.filter(
        action="accounts.user.read",
        target_model="accounts.User",
        target_id=str(target_user.pk),
        actor=staff,
        metadata__scope="detail",
    ).exists()


@pytest.mark.django_db
def test_deactivate_me_deactivates_user_and_writes_audit_event(api_client):
    user = UserFactory(is_active=True)
    api_client.force_authenticate(user=user)

    response = api_client.post(reverse("accounts-user-deactivate-me"))

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.is_active is False
    assert AuditEvent.objects.filter(
        action="accounts.user.deactivated",
        target_model="accounts.User",
        target_id=str(user.pk),
        actor=user,
        metadata__source="api",
    ).exists()
