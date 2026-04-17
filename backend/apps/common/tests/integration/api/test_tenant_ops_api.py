import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from apps.common.models import TenantMembership
from apps.common.tests.factories import TenantFactory, UserFactory


@pytest.mark.django_db
def test_tenant_ops_requires_operator_permission(api_client):
    user = UserFactory(is_staff=True)
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("common-tenant-ops-list"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_tenant_ops_create_tenant_for_operator(api_client):
    user = UserFactory(is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="operate_auditevent"))
    api_client.force_authenticate(user=user)

    response = api_client.post(
        reverse("common-tenant-ops-list"),
        data={"slug": "acme", "name": "Acme", "status": "active", "settings": {}},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["slug"] == "acme"


@pytest.mark.django_db
def test_tenant_membership_ops_assign_user_to_tenant(api_client):
    operator = UserFactory(is_staff=True)
    operator.user_permissions.add(Permission.objects.get(codename="operate_auditevent"))
    api_client.force_authenticate(user=operator)
    tenant = TenantFactory(slug="tenant-a")
    target_user = UserFactory()

    response = api_client.post(
        reverse("common-tenant-membership-ops-list"),
        data={
            "tenant_id": str(tenant.pk),
            "user_id": target_user.pk,
            "role": "member",
            "is_active": True,
        },
        format="json",
    )

    assert response.status_code == 201
    assert TenantMembership.objects.filter(tenant=tenant, user=target_user, is_active=True).exists()
