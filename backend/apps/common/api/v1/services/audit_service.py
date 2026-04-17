from __future__ import annotations

import hashlib
import json
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.common.exceptions import InvalidAuditEvent
from apps.common.models import AuditChainState, AuditEvent

_SENSITIVE_METADATA_KEYS = {
    "password",
    "token",
    "secret",
    "authorization",
    "api_key",
    "access_token",
    "refresh_token",
}


def _normalize_target_id(target_id: str) -> str:
    normalized = str(target_id).strip()
    if not normalized:
        raise InvalidAuditEvent("target_id must not be empty")
    return normalized


def _normalize_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    normalized = _sanitize_metadata(metadata or {})
    source = normalized.get("source")
    if not isinstance(source, str) or not source.strip():
        normalized["source"] = "system"
    normalized["request_id"] = normalized.get("request_id")
    normalized["trace_id"] = normalized.get("trace_id")
    return normalized


def _calculate_integrity_hash(
    *,
    action: str,
    target_model: str,
    target_id: str,
    actor_id: int | None,
    metadata: dict[str, Any],
    ip_address: str | None,
    user_agent: str,
    previous_hash: str,
) -> str:
    payload = {
        "action": action,
        "target_model": target_model,
        "target_id": target_id,
        "actor_id": actor_id,
        "metadata": metadata,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "previous_hash": previous_hash,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _sanitize_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if key.lower() in _SENSITIVE_METADATA_KEYS:
                continue
            sanitized[key] = _sanitize_metadata(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_metadata(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _lock_chain_state() -> AuditChainState:
    chain_state, _ = AuditChainState.objects.select_for_update().get_or_create(
        pk=AuditChainState.SINGLETON_PK,
    )
    if chain_state.last_hash:
        return chain_state

    latest_hash = (
        AuditEvent.objects.order_by("-created_at", "-id")
        .values_list("integrity_hash", flat=True)
        .first()
        or ""
    )
    if chain_state.last_hash != latest_hash:
        chain_state.last_hash = latest_hash
        chain_state.updated_at = timezone.now()
        chain_state.save(update_fields=("last_hash", "updated_at"))
    return chain_state


def record_audit_event(
    *,
    action: str,
    target_model: str,
    target_id: str,
    actor=None,
    metadata: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str = "",
    request_id: str | None = None,
    trace_id: str | None = None,
) -> AuditEvent:
    if not action.strip():
        raise InvalidAuditEvent("action must not be empty")
    if not target_model.strip():
        raise InvalidAuditEvent("target_model must not be empty")

    normalized_target_id = _normalize_target_id(target_id)
    merged_metadata = dict(metadata or {})
    if request_id is not None:
        merged_metadata["request_id"] = request_id
    if trace_id is not None:
        merged_metadata["trace_id"] = trace_id
    normalized_metadata = _normalize_metadata(merged_metadata)

    with transaction.atomic():
        chain_state = _lock_chain_state()
        previous_hash = chain_state.last_hash
        integrity_hash = _calculate_integrity_hash(
            action=action,
            target_model=target_model,
            target_id=normalized_target_id,
            actor_id=getattr(actor, "id", None),
            metadata=normalized_metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            previous_hash=previous_hash,
        )

        event = AuditEvent.objects.create(
            actor=actor,
            action=action,
            target_model=target_model,
            target_id=normalized_target_id,
            metadata=normalized_metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            previous_hash=previous_hash,
            integrity_hash=integrity_hash,
        )
        chain_state.last_hash = integrity_hash
        chain_state.updated_at = timezone.now()
        chain_state.save(update_fields=("last_hash", "updated_at"))
        return event
