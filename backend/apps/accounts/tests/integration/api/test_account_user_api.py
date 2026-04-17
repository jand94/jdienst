import pytest
from django.urls import reverse

from apps.common.models import AuditEvent
from apps.common.tests.factories import TenantMembershipFactory, TenantFactory, UserFactory


@pytest.mark.django_db
def test_list_users_requires_staff_permission(api_client):
    user = UserFactory(is_staff=False)
    tenant = TenantFactory()
    TenantMembershipFactory(user=user, tenant=tenant)
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("accounts-user-list"), HTTP_X_TENANT_SLUG=tenant.slug)

    assert response.status_code == 403


@pytest.mark.django_db
def test_list_users_returns_paginated_results_for_staff(api_client):
    staff_user = UserFactory(is_staff=True)
    tenant = TenantFactory()
    TenantMembershipFactory(user=staff_user, tenant=tenant, role="admin")
    for member in UserFactory.create_batch(3):
        TenantMembershipFactory(user=member, tenant=tenant)
    api_client.force_authenticate(user=staff_user)

    response = api_client.get(reverse("accounts-user-list"), HTTP_X_TENANT_SLUG=tenant.slug)

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
    tenant = TenantFactory()
    TenantMembershipFactory(user=user, tenant=tenant)
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("accounts-user-me"), HTTP_X_TENANT_SLUG=tenant.slug)

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
    tenant = TenantFactory()
    TenantMembershipFactory(user=user, tenant=tenant)
    api_client.force_authenticate(user=user)

    response = api_client.patch(
        reverse("accounts-user-me"),
        data={"first_name": "New"},
        format="json",
        HTTP_IDEMPOTENCY_KEY="me-patch-1",
        HTTP_X_TENANT_SLUG=tenant.slug,
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
def test_patch_me_requires_idempotency_key(api_client):
    user = UserFactory(first_name="Old")
    tenant = TenantFactory()
    TenantMembershipFactory(user=user, tenant=tenant)
    api_client.force_authenticate(user=user)

    response = api_client.patch(
        reverse("accounts-user-me"),
        data={"first_name": "New"},
        format="json",
        HTTP_X_TENANT_SLUG=tenant.slug,
    )

    assert response.status_code == 400
    assert response.data["error"]["code"] == "validation_error"


@pytest.mark.django_db
def test_retrieve_foreign_user_is_forbidden_and_audited(api_client):
    actor = UserFactory()
    other_user = UserFactory()
    tenant = TenantFactory()
    TenantMembershipFactory(user=actor, tenant=tenant)
    TenantMembershipFactory(user=other_user, tenant=tenant)
    api_client.force_authenticate(user=actor)

    response = api_client.get(
        reverse("accounts-user-detail", kwargs={"pk": other_user.pk}),
        HTTP_X_TENANT_SLUG=tenant.slug,
    )

    assert response.status_code == 403
    assert response.data["error"]["code"] == "permission_denied"
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
    tenant = TenantFactory()
    TenantMembershipFactory(user=staff, tenant=tenant, role="admin")
    TenantMembershipFactory(user=target_user, tenant=tenant)
    api_client.force_authenticate(user=staff)

    response = api_client.get(
        reverse("accounts-user-detail", kwargs={"pk": target_user.pk}),
        HTTP_X_TENANT_SLUG=tenant.slug,
    )

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
    tenant = TenantFactory()
    TenantMembershipFactory(user=user, tenant=tenant)
    api_client.force_authenticate(user=user)

    response = api_client.post(
        reverse("accounts-user-deactivate-me"),
        HTTP_IDEMPOTENCY_KEY="deactivate-1",
        HTTP_X_TENANT_SLUG=tenant.slug,
    )

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


@pytest.mark.django_db
def test_deactivate_me_replays_response_for_same_idempotency_key(api_client):
    user = UserFactory(is_active=True)
    tenant = TenantFactory()
    TenantMembershipFactory(user=user, tenant=tenant)
    api_client.force_authenticate(user=user)
    url = reverse("accounts-user-deactivate-me")

    first = api_client.post(url, HTTP_IDEMPOTENCY_KEY="deactivate-2", HTTP_X_TENANT_SLUG=tenant.slug)
    second = api_client.post(url, HTTP_IDEMPOTENCY_KEY="deactivate-2", HTTP_X_TENANT_SLUG=tenant.slug)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second["X-Idempotent-Replayed"] == "true"
    assert (
        AuditEvent.objects.filter(
            action="accounts.user.deactivated",
            target_model="accounts.User",
            target_id=str(user.pk),
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_me_endpoint_rejects_user_without_tenant_membership(api_client):
    user = UserFactory()
    tenant = TenantFactory()
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("accounts-user-me"), HTTP_X_TENANT_SLUG=tenant.slug)

    assert response.status_code == 403


@pytest.mark.django_db
def test_me_tenants_returns_active_memberships_without_tenant_header(api_client):
    user = UserFactory()
    tenant_a = TenantFactory(slug="tenant-a", name="Tenant A")
    tenant_b = TenantFactory(slug="tenant-b", name="Tenant B")
    TenantMembershipFactory(user=user, tenant=tenant_a, role="owner", is_active=True)
    TenantMembershipFactory(user=user, tenant=tenant_b, role="member", is_active=False)
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("accounts-user-me-tenants"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["tenant_slug"] == "tenant-a"
    assert response.data[0]["role"] == "owner"
    assert response.data[0]["is_active"] is True


@pytest.mark.django_db
def test_retrieve_user_from_another_tenant_is_hidden(api_client):
    staff = UserFactory(is_staff=True)
    tenant_a = TenantFactory(slug="tenant-a")
    tenant_b = TenantFactory(slug="tenant-b")
    target_user = UserFactory()
    TenantMembershipFactory(user=staff, tenant=tenant_a, role="admin")
    TenantMembershipFactory(user=target_user, tenant=tenant_b)
    api_client.force_authenticate(user=staff)

    response = api_client.get(
        reverse("accounts-user-detail", kwargs={"pk": target_user.pk}),
        HTTP_X_TENANT_SLUG=tenant_a.slug,
    )

    assert response.status_code == 404
