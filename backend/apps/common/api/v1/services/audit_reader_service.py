from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import Group, Permission

from apps.common.api.v1.services.audit_service import record_audit_event


def is_audit_reader(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.has_perm("common.view_auditevent"):
        return True

    configured_groups = getattr(settings, "AUDIT_READER_GROUPS", [])
    if not configured_groups:
        return False
    return user.groups.filter(name__in=configured_groups).exists()


def is_audit_operator(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if user.has_perm("common.operate_auditevent"):
        return True

    configured_groups = getattr(settings, "AUDIT_OPERATOR_GROUPS", [])
    if not configured_groups:
        return False
    return user.groups.filter(name__in=configured_groups).exists()


def log_audit_reader_access(
    *,
    actor,
    access_type: str,
    target_id: str = "",
    source: str = "api",
    metadata: dict | None = None,
    request_id: str | None = None,
    trace_id: str | None = None,
):
    payload = {"source": source, "access_type": access_type}
    if metadata:
        payload.update(metadata)
    return record_audit_event(
        action="common.audit_event.read",
        target_model="common.AuditEvent",
        target_id=target_id or "collection",
        actor=actor,
        metadata=payload,
        request_id=request_id,
        trace_id=trace_id,
    )


def ensure_audit_reader_roles() -> tuple[list[str], int]:
    role_names = getattr(settings, "AUDIT_READER_GROUPS", ["AuditReader"])
    permission = Permission.objects.get(codename="view_auditevent")
    created_total = 0
    for role_name in role_names:
        group, created = Group.objects.get_or_create(name=role_name)
        group.permissions.add(permission)
        created_total += int(created)
    return role_names, created_total


def ensure_audit_operator_roles() -> tuple[list[str], int]:
    role_names = getattr(settings, "AUDIT_OPERATOR_GROUPS", ["AuditOperator"])
    permission = Permission.objects.get(codename="operate_auditevent")
    created_total = 0
    for role_name in role_names:
        group, created = Group.objects.get_or_create(name=role_name)
        group.permissions.add(permission)
        created_total += int(created)
    return role_names, created_total
