import pytest

from apps.common.api.v1.services.tenant_authorization_service import (
    resolve_role_feature_flags,
    resolve_role_permissions,
)
from apps.common.tests.factories import TenantFactory


@pytest.mark.django_db
def test_resolve_role_permissions_includes_tenant_overrides():
    tenant = TenantFactory(
        settings={
            "rbac": {
                "role_permissions": {
                    "member": ["reports.export"],
                }
            }
        }
    )

    permissions = resolve_role_permissions(role="member", tenant=tenant)

    assert "reports.export" in permissions


@pytest.mark.django_db
def test_resolve_role_feature_flags_reads_tenant_config():
    tenant = TenantFactory(
        settings={
            "rbac": {
                "feature_flags": {
                    "owner": ["advanced_audit_console"],
                }
            }
        }
    )

    flags = resolve_role_feature_flags(role="owner", tenant=tenant)

    assert "advanced_audit_console" in flags
