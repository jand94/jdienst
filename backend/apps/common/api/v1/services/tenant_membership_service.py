from __future__ import annotations

from django.conf import settings
from django.db import transaction

from apps.common.api.v1.services.audit_service import record_audit_event
from apps.common.models import Tenant, TenantMembership


@transaction.atomic
def assign_user_to_tenant(
    *,
    user,
    tenant: Tenant,
    role: str = TenantMembership.ROLE_MEMBER,
    is_active: bool = True,
    actor=None,
    source: str = "api",
    request_id: str | None = None,
    trace_id: str | None = None,
) -> TenantMembership:
    membership, created = TenantMembership.objects.get_or_create(
        tenant=tenant,
        user=user,
        defaults={
            "role": role,
            "is_active": is_active,
        },
    )
    changed = []
    if not created and membership.role != role:
        membership.role = role
        changed.append("role")
    if not created and membership.is_active != is_active:
        membership.is_active = is_active
        changed.append("is_active")
    if changed:
        membership.save(update_fields=tuple(changed) + ("updated_at",))

    action = "common.tenant_membership.created" if created else "common.tenant_membership.updated"
    if created or changed:
        record_audit_event(
            action=action,
            target_model="common.TenantMembership",
            target_id=str(membership.pk),
            actor=actor if getattr(actor, "is_authenticated", False) else None,
            metadata={
                "source": source,
                "tenant_id": str(tenant.pk),
                "tenant_slug": tenant.slug,
                "user_id": str(user.pk),
                "role": membership.role,
                "is_active": membership.is_active,
            },
            request_id=request_id,
            trace_id=trace_id,
        )
    return membership


def deactivate_tenant_membership(
    *,
    membership: TenantMembership,
    actor=None,
    source: str = "api",
    request_id: str | None = None,
    trace_id: str | None = None,
) -> TenantMembership:
    if membership.is_active:
        membership.is_active = False
        membership.save(update_fields=("is_active", "updated_at"))
        record_audit_event(
            action="common.tenant_membership.deactivated",
            target_model="common.TenantMembership",
            target_id=str(membership.pk),
            actor=actor if getattr(actor, "is_authenticated", False) else None,
            metadata={
                "source": source,
                "tenant_id": str(membership.tenant_id),
                "user_id": str(membership.user_id),
            },
            request_id=request_id,
            trace_id=trace_id,
        )
    return membership


def assign_user_to_default_tenant(
    *,
    user,
    actor=None,
    source: str = "user_create",
    request_id: str | None = None,
    trace_id: str | None = None,
) -> TenantMembership | None:
    if not getattr(settings, "COMMON_TENANT_AUTO_ASSIGN_ON_USER_CREATE", False):
        return None
    default_slug = getattr(settings, "COMMON_TENANT_DEFAULT_SLUG", "").strip()
    if not default_slug:
        return None
    tenant = Tenant.objects.filter(slug=default_slug, status=Tenant.STATUS_ACTIVE).first()
    if tenant is None:
        return None
    role = getattr(settings, "COMMON_TENANT_DEFAULT_ROLE", TenantMembership.ROLE_MEMBER)
    return assign_user_to_tenant(
        user=user,
        tenant=tenant,
        role=role,
        is_active=True,
        actor=actor,
        source=source,
        request_id=request_id,
        trace_id=trace_id,
    )
