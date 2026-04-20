from __future__ import annotations

from apps.common.models import Tenant, TenantMembership

_TENANT_ROLE_PERMISSIONS: dict[str, set[str]] = {
    TenantMembership.ROLE_MEMBER: set(),
    TenantMembership.ROLE_ADMIN: {"tenant.members.manage"},
    TenantMembership.ROLE_OWNER: {"tenant.members.manage", "tenant.settings.manage"},
}


def _tenant_rbac_settings(tenant: Tenant) -> dict:
    settings_payload = tenant.settings or {}
    rbac = settings_payload.get("rbac", {})
    if isinstance(rbac, dict):
        return rbac
    return {}


def resolve_role_permissions(*, role: str | None, tenant: Tenant) -> set[str]:
    if not role:
        return set()
    permissions = set(_TENANT_ROLE_PERMISSIONS.get(role, set()))
    role_overrides = _tenant_rbac_settings(tenant).get("role_permissions", {})
    if isinstance(role_overrides, dict):
        custom = role_overrides.get(role, [])
        if isinstance(custom, list):
            permissions.update(item for item in custom if isinstance(item, str) and item.strip())
    return permissions


def resolve_role_feature_flags(*, role: str | None, tenant: Tenant) -> set[str]:
    if not role:
        return set()
    feature_flags = _tenant_rbac_settings(tenant).get("feature_flags", {})
    if not isinstance(feature_flags, dict):
        return set()
    selected = feature_flags.get(role, [])
    if not isinstance(selected, list):
        return set()
    return {item for item in selected if isinstance(item, str) and item.strip()}
