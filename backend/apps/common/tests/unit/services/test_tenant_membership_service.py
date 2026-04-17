import pytest
from django.test import override_settings

from apps.common.api.v1.services import assign_user_to_default_tenant, assign_user_to_tenant
from apps.common.models import TenantMembership
from apps.common.tests.factories import TenantFactory, UserFactory


@pytest.mark.django_db
def test_assign_user_to_tenant_creates_membership():
    tenant = TenantFactory()
    user = UserFactory()

    membership = assign_user_to_tenant(user=user, tenant=tenant, role=TenantMembership.ROLE_ADMIN)

    assert membership.user_id == user.id
    assert membership.tenant_id == tenant.id
    assert membership.role == TenantMembership.ROLE_ADMIN


@pytest.mark.django_db
@override_settings(
    COMMON_TENANT_AUTO_ASSIGN_ON_USER_CREATE=True,
    COMMON_TENANT_DEFAULT_SLUG="default-tenant",
    COMMON_TENANT_DEFAULT_ROLE="member",
)
def test_assign_user_to_default_tenant_uses_settings():
    tenant = TenantFactory(slug="default-tenant")
    user = UserFactory()

    membership = assign_user_to_default_tenant(user=user)

    assert membership is not None
    assert membership.tenant_id == tenant.id
    assert membership.user_id == user.id
