import pytest
from django.test import override_settings

from apps.common.models import TenantMembership
from apps.common.tests.factories import TenantFactory, UserFactory


@pytest.mark.django_db
@override_settings(
    COMMON_TENANT_AUTO_ASSIGN_ON_USER_CREATE=True,
    COMMON_TENANT_DEFAULT_SLUG="bootstrap",
    COMMON_TENANT_DEFAULT_ROLE="member",
)
def test_user_create_signal_assigns_default_tenant_membership():
    tenant = TenantFactory(slug="bootstrap")
    user = UserFactory()

    assert TenantMembership.objects.filter(user=user, tenant=tenant, is_active=True).exists()
