import pytest

from apps.common.api.v1.services.tenant_isolation_service import tenant_scoped_queryset
from apps.common.exceptions import InfrastructureError
from apps.common.models import Tenant, TenantMembership
from apps.common.tests.factories import TenantFactory, TenantMembershipFactory, UserFactory


@pytest.mark.django_db
def test_tenant_scoped_queryset_filters_by_tenant_field():
    tenant_a = TenantFactory()
    tenant_b = TenantFactory()
    TenantMembershipFactory(user=UserFactory(), tenant=tenant_a, is_active=True)
    TenantMembershipFactory(user=UserFactory(), tenant=tenant_b, is_active=True)

    queryset = tenant_scoped_queryset(queryset=TenantMembership.objects.all(), tenant=tenant_a)

    assert queryset.count() == 1
    assert queryset.first().tenant_id == tenant_a.id


@pytest.mark.django_db
def test_tenant_scoped_queryset_raises_for_missing_field():
    tenant = TenantFactory()

    with pytest.raises(InfrastructureError):
        tenant_scoped_queryset(
            queryset=Tenant.objects.all(),
            tenant=tenant,
            field_name="tenant",
        )
