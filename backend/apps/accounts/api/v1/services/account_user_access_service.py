from __future__ import annotations

from apps.accounts.models import User
from apps.common.api.v1.services import is_audit_operator, is_audit_reader
from apps.common.models import Tenant, TenantMembership

_BASE_PERMISSIONS = {
    "dashboard.view",
    "reports.view",
    "settings.view",
    "accounts.self.read",
    "accounts.self.update",
    "accounts.tenants.read",
}

_TENANT_ROLE_PERMISSIONS: dict[str, set[str]] = {
    TenantMembership.ROLE_MEMBER: set(),
    TenantMembership.ROLE_ADMIN: {"tenant.members.manage"},
    TenantMembership.ROLE_OWNER: {"tenant.members.manage", "tenant.settings.manage"},
}

_STAFF_EXTRA_PERMISSIONS = {
    "tenant.members.manage",
    "tenant.settings.manage",
}

_AUDIT_READER_PERMISSION = "audit.events.read"
_AUDIT_OPERATOR_PERMISSION = "audit.ops.manage"

_FEATURE_FLAG_DYNAMIC_AUTHZ = "dynamic_authz_navigation"
_FEATURE_FLAG_AUDIT_OPS = "audit_ops_enabled"


def _resolve_membership_role(*, user: User, tenant: Tenant) -> str | None:
    membership = (
        TenantMembership.objects.filter(user=user, tenant=tenant, is_active=True)
        .values_list("role", flat=True)
        .first()
    )
    if isinstance(membership, str) and membership:
        return membership
    return None


def resolve_user_access_context(*, user: User, tenant: Tenant) -> dict[str, list[str] | str | None]:
    current_tenant_role = _resolve_membership_role(user=user, tenant=tenant)
    permissions = set(_BASE_PERMISSIONS)
    if current_tenant_role:
        permissions.update(_TENANT_ROLE_PERMISSIONS.get(current_tenant_role, set()))
    if user.is_staff:
        permissions.update(_STAFF_EXTRA_PERMISSIONS)
    if is_audit_reader(user):
        permissions.add(_AUDIT_READER_PERMISSION)
    if is_audit_operator(user):
        permissions.add(_AUDIT_OPERATOR_PERMISSION)

    feature_flags = {_FEATURE_FLAG_DYNAMIC_AUTHZ}
    if _AUDIT_OPERATOR_PERMISSION in permissions:
        feature_flags.add(_FEATURE_FLAG_AUDIT_OPS)

    return {
        "permissions": sorted(permissions),
        "feature_flags": sorted(feature_flags),
        "current_tenant_role": current_tenant_role,
    }
