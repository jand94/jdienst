from __future__ import annotations

import hashlib
import json
from typing import Any

from django.db import transaction

from apps.common.exceptions import InvalidAuditEvent
from apps.common.models import AuditEvent

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
    if "source" not in normalized:
        normalized["source"] = "system"
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


def record_audit_event(
    *,
    action: str,
    target_model: str,
    target_id: str,
    actor=None,
    metadata: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str = "",
) -> AuditEvent:
    if not action.strip():
        raise InvalidAuditEvent("action must not be empty")
    if not target_model.strip():
        raise InvalidAuditEvent("target_model must not be empty")

    normalized_target_id = _normalize_target_id(target_id)
    normalized_metadata = _normalize_metadata(metadata)

    with transaction.atomic():
        previous_event = AuditEvent.objects.order_by("-created_at", "-id").first()
        previous_hash = previous_event.integrity_hash if previous_event else ""
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

        return AuditEvent.objects.create(
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
