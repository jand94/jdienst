from django.db import transaction

from apps.accounts.models import User
from apps.common.api.v1.services import record_audit_event

_PROFILE_UPDATE_FIELDS = ("first_name", "last_name", "email")


def update_user_profile(*, actor: User, data: dict, source: str) -> User:
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
            )
    return actor


def deactivate_user(*, actor: User, source: str, reason: str = "self-service") -> User:
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
        )
    return actor


def log_user_list_access(*, actor: User, source: str) -> None:
    record_audit_event(
        action="accounts.user.listed",
        target_model="accounts.User",
        target_id=str(actor.pk),
        actor=actor,
        metadata={"source": source},
    )


def log_user_read_access(*, actor: User, target: User, source: str, scope: str) -> None:
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
    )
