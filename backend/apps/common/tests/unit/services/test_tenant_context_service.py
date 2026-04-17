import pytest
from types import SimpleNamespace
from django.test import override_settings

from apps.common.api.v1.services.tenant_context_service import (
    ensure_user_in_tenant,
    resolve_request_tenant,
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


@pytest.mark.django_db
@override_settings(COMMON_TENANT_HEADER_REQUIRED=False, COMMON_TENANT_DEFAULT_SLUG="default-tenant")
def test_resolve_request_tenant_falls_back_to_default_slug():
    tenant = TenantFactory(slug="default-tenant")
    request = SimpleNamespace(headers={}, user=None)

    resolved = resolve_request_tenant(request)

    assert resolved is not None
    assert resolved.pk == tenant.pk


@pytest.mark.django_db
@override_settings(COMMON_TENANT_AUTO_RESOLVE_SINGLE_MEMBERSHIP=True, COMMON_TENANT_HEADER_REQUIRED=True)
def test_resolve_request_tenant_uses_single_membership_when_enabled():
    tenant = TenantFactory(slug="single-tenant")
    user = UserFactory()
    TenantMembershipFactory(user=user, tenant=tenant, is_active=True)
    request = SimpleNamespace(headers={}, user=user)

    resolved = resolve_request_tenant(request)

    assert resolved is not None
    assert resolved.pk == tenant.pk
