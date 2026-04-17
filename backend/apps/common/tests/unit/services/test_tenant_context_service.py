import pytest
from types import SimpleNamespace

from apps.common.api.v1.services.tenant_context_service import (
    ensure_user_in_tenant,
    require_tenant,
)
from apps.common.exceptions import SecurityError, ValidationError
from apps.common.tests.factories import TenantFactory, TenantMembershipFactory, UserFactory


@pytest.mark.django_db
def test_require_tenant_reads_slug_header():
    tenant = TenantFactory(slug="acme")
    request = SimpleNamespace(headers={"X-Tenant-Slug": "acme"})

    resolved = require_tenant(request)

    assert resolved.pk == tenant.pk


@pytest.mark.django_db
def test_require_tenant_raises_on_missing_header():
    request = SimpleNamespace(headers={})

    with pytest.raises(ValidationError):
        require_tenant(request)


@pytest.mark.django_db
def test_ensure_user_in_tenant_requires_membership():
    tenant = TenantFactory()
    user = UserFactory()

    with pytest.raises(SecurityError):
        ensure_user_in_tenant(user=user, tenant=tenant)

    TenantMembershipFactory(user=user, tenant=tenant)
    ensure_user_in_tenant(user=user, tenant=tenant)
