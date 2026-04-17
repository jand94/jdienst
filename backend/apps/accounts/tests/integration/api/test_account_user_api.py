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


@pytest.mark.django_db
def test_me_endpoint_returns_authenticated_user(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("accounts-user-me"))

    assert response.status_code == 200
    assert response.data["id"] == user.id
    assert response.data["username"] == user.username


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
