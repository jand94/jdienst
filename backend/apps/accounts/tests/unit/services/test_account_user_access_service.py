import pytest
from django.contrib.auth.models import Permission

from apps.accounts.api.v1.services.account_user_access_service import resolve_user_access_context
from apps.common.tests.factories import TenantFactory, TenantMembershipFactory, UserFactory


@pytest.mark.django_db
def test_resolve_user_access_context_for_member_role():
    user = UserFactory(is_staff=False)
    tenant = TenantFactory()
    TenantMembershipFactory(user=user, tenant=tenant, role="member", is_active=True)

    access = resolve_user_access_context(user=user, tenant=tenant)

    assert access["current_tenant_role"] == "member"
    assert "settings.view" in access["permissions"]
    assert "tenant.settings.manage" not in access["permissions"]
    assert "audit.events.read" not in access["permissions"]
    assert "dynamic_authz_navigation" in access["feature_flags"]


@pytest.mark.django_db
def test_resolve_user_access_context_for_owner_with_audit_permissions():
    user = UserFactory(is_staff=False)
    tenant = TenantFactory()
    TenantMembershipFactory(user=user, tenant=tenant, role="owner", is_active=True)
    user.user_permissions.add(Permission.objects.get(codename="view_auditevent"))
    user.user_permissions.add(Permission.objects.get(codename="operate_auditevent"))

    access = resolve_user_access_context(user=user, tenant=tenant)

    assert access["current_tenant_role"] == "owner"
    assert "tenant.settings.manage" in access["permissions"]
    assert "audit.events.read" in access["permissions"]
    assert "audit.ops.manage" in access["permissions"]
    assert "audit_ops_enabled" in access["feature_flags"]


@pytest.mark.django_db
def test_resolve_user_access_context_applies_tenant_rbac_overrides():
    user = UserFactory(is_staff=False)
    tenant = TenantFactory(
        settings={
            "rbac": {
                "role_permissions": {"member": ["reports.export"]},
                "feature_flags": {"member": ["dynamic_reports"]},
            }
        }
    )
    TenantMembershipFactory(user=user, tenant=tenant, role="member", is_active=True)

    access = resolve_user_access_context(user=user, tenant=tenant)

    assert "reports.export" in access["permissions"]
    assert "dynamic_reports" in access["feature_flags"]
