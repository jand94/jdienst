import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from apps.common.tests.factories import TenantFactory, UserFactory


@pytest.mark.django_db
def test_platform_health_requires_operator_permission(api_client):
    user = UserFactory(is_staff=True)
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("common-platform-health-snapshot"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_platform_health_returns_snapshot_for_operator(api_client):
    user = UserFactory(is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="operate_auditevent"))
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("common-platform-health-snapshot"), {"window_hours": 24})

    assert response.status_code == 200
    assert "audit" in response.data
    assert "idempotency" in response.data
    assert "outbox" in response.data


@pytest.mark.django_db
def test_platform_ops_check_returns_result(api_client):
    user = UserFactory(is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="operate_auditevent"))
    api_client.force_authenticate(user=user)

    response = api_client.post(
        reverse("common-platform-ops-check"),
        data={"window_hours": 24},
        format="json",
    )

    assert response.status_code == 200
    assert "passed" in response.data
    assert "checks" in response.data


@pytest.mark.django_db
def test_platform_ops_tenant_consistency_returns_payload(api_client):
    user = UserFactory(is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="operate_auditevent"))
    api_client.force_authenticate(user=user)

    response = api_client.post(reverse("common-platform-ops-tenant-consistency"), data={}, format="json")

    assert response.status_code == 200
    assert "passed" in response.data
    assert "tenant_count" in response.data


@pytest.mark.django_db
def test_platform_ops_soft_delete_cleanup_returns_count(api_client):
    user = UserFactory(is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="operate_auditevent"))
    api_client.force_authenticate(user=user)
    TenantFactory().soft_delete(reason="cleanup")

    response = api_client.post(
        reverse("common-platform-ops-soft-delete-cleanup"),
        data={"older_than_days": 1},
        format="json",
    )

    assert response.status_code == 200
    assert "cleaned_records" in response.data
