from django.db import transaction

from apps.accounts.models import User
from apps.common.api.v1.services import (
    assign_user_to_tenant,
    enqueue_outbox_event,
    record_audit_event,
)
from apps.common.models import TenantMembership

_PROFILE_UPDATE_FIELDS = ("first_name", "last_name", "email")


def update_user_profile(
    *,
    actor: User,
    data: dict,
    source: str,
    request_id: str | None = None,
    trace_id: str | None = None,
) -> User:
    changed_fields: dict[str, dict[str, str]] = {}
    for field in _PROFILE_UPDATE_FIELDS:
        if field not in data:
            continue
        old_value = getattr(actor, field)
        new_value = data[field]
        if old_value == new_value:
            continue
        setattr(actor, field, new_value)
        changed_fields[field] = {"old": old_value, "new": new_value}

    if changed_fields:
        with transaction.atomic():
            actor.save(update_fields=tuple(changed_fields.keys()))
            record_audit_event(
                action="accounts.user.updated",
                target_model="accounts.User",
                target_id=str(actor.pk),
                actor=actor,
                metadata={
                    "source": source,
                    "changes": changed_fields,
                },
                request_id=request_id,
                trace_id=trace_id,
            )
            enqueue_outbox_event(
                topic="accounts.user.updated",
                dedup_key=f"accounts.user.updated:{actor.pk}:{','.join(sorted(changed_fields.keys()))}",
                headers={
                    "request_id": request_id,
                    "trace_id": trace_id,
                },
                payload={
                    "user_id": str(actor.pk),
                    "changed_fields": sorted(changed_fields.keys()),
                    "source": source,
                },
            )
    return actor


def deactivate_user(
    *,
    actor: User,
    source: str,
    reason: str = "self-service",
    request_id: str | None = None,
    trace_id: str | None = None,
) -> User:
    if not actor.is_active:
        return actor

    with transaction.atomic():
        actor.is_active = False
        actor.save(update_fields=("is_active",))
        record_audit_event(
            action="accounts.user.deactivated",
            target_model="accounts.User",
            target_id=str(actor.pk),
            actor=actor,
            metadata={"source": source, "reason": reason},
            request_id=request_id,
            trace_id=trace_id,
        )
        enqueue_outbox_event(
            topic="accounts.user.deactivated",
            dedup_key=f"accounts.user.deactivated:{actor.pk}",
            headers={
                "request_id": request_id,
                "trace_id": trace_id,
            },
            payload={
                "user_id": str(actor.pk),
                "reason": reason,
                "source": source,
            },
        )
    return actor


def assign_user_to_tenant_membership(
    *,
    actor: User,
    target_user: User,
    tenant,
    role: str = TenantMembership.ROLE_MEMBER,
    source: str,
    request_id: str | None = None,
    trace_id: str | None = None,
):
    return assign_user_to_tenant(
        user=target_user,
        tenant=tenant,
        role=role,
        is_active=True,
        actor=actor,
        source=source,
        request_id=request_id,
        trace_id=trace_id,
    )


def log_user_list_access(
    *,
    actor: User,
    source: str,
    request_id: str | None = None,
    trace_id: str | None = None,
) -> None:
    record_audit_event(
        action="accounts.user.listed",
        target_model="accounts.User",
        target_id=str(actor.pk),
        actor=actor,
        metadata={"source": source},
        request_id=request_id,
        trace_id=trace_id,
    )


def log_user_read_access(
    *,
    actor: User,
    target: User,
    source: str,
    scope: str,
    request_id: str | None = None,
    trace_id: str | None = None,
) -> None:
    record_audit_event(
        action="accounts.user.read",
        target_model="accounts.User",
        target_id=str(target.pk),
        actor=actor,
        metadata={
            "source": source,
            "scope": scope,
            "is_self": actor.pk == target.pk,
        },
        request_id=request_id,
        trace_id=trace_id,
    )
