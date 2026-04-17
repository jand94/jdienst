from __future__ import annotations

from contextvars import ContextVar

from django.conf import settings

from apps.common.constants import HeaderName
from apps.common.exceptions import SecurityError, ValidationError
from apps.common.models import Tenant, TenantMembership

_TENANT_CONTEXT: ContextVar[dict] = ContextVar("common_tenant_context", default={})


def set_tenant_context(payload: dict) -> None:
    _TENANT_CONTEXT.set(payload)


def get_tenant_context() -> dict:
    return dict(_TENANT_CONTEXT.get())


def clear_tenant_context() -> None:
    _TENANT_CONTEXT.set({})


def extract_tenant_slug(request) -> str | None:
    headers = getattr(request, "headers", {})
    value = headers.get(HeaderName.TENANT_SLUG.value, "")
    normalized = value.strip() if isinstance(value, str) else ""
    return normalized or None


def _resolve_single_membership_tenant(*, user) -> Tenant | None:
    if user is None or not getattr(user, "is_authenticated", False):
        return None
    if not getattr(settings, "COMMON_TENANT_AUTO_RESOLVE_SINGLE_MEMBERSHIP", False):
        return None
    memberships = list(
        TenantMembership.objects.select_related("tenant")
        .filter(user=user, is_active=True, tenant__status=Tenant.STATUS_ACTIVE)
        .order_by("created_at")[:2]
    )
    if len(memberships) != 1:
        return None
    return memberships[0].tenant


def resolve_request_tenant(request) -> Tenant | None:
    # Resolution order is explicit and deterministic:
    # 1) X-Tenant-Slug header
    # 2) optional single-membership auto resolution (disabled by default)
    # 3) global default tenant slug (when headers are not required)
    slug = extract_tenant_slug(request)
    if slug:
        return Tenant.objects.filter(slug=slug, status=Tenant.STATUS_ACTIVE).first()
    tenant_from_membership = _resolve_single_membership_tenant(user=getattr(request, "user", None))
    if tenant_from_membership is not None:
        return tenant_from_membership
    if getattr(settings, "COMMON_TENANT_HEADER_REQUIRED", True):
        return None
    slug = getattr(settings, "COMMON_TENANT_DEFAULT_SLUG", "").strip()
    if not slug:
        return None
    return Tenant.objects.filter(slug=slug, status=Tenant.STATUS_ACTIVE).first()


def ensure_user_in_tenant(*, user, tenant: Tenant) -> None:
    if user is None or not getattr(user, "is_authenticated", False):
        raise SecurityError("Authentication is required for tenant-scoped access.")
    if user.is_superuser:
        return
    membership_exists = TenantMembership.objects.filter(
        tenant=tenant,
        user=user,
        is_active=True,
    ).exists()
    if not membership_exists:
        raise SecurityError(
            "User is not a member of the requested tenant.",
            details={"tenant": tenant.slug},
        )


def require_tenant(request) -> Tenant:
    tenant = resolve_request_tenant(request)
    if tenant is None:
        raise ValidationError(
            "X-Tenant-Slug header is required and must reference an active tenant.",
            details={"header": HeaderName.TENANT_SLUG.value},
        )
    return tenant
