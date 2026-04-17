from __future__ import annotations

from django.conf import settings

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


def log_audit_reader_access(
    *,
    actor,
    access_type: str,
    target_id: str = "",
    source: str = "api",
    metadata: dict | None = None,
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
    )
