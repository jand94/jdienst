from __future__ import annotations

from typing import Any

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
    if not target_id.strip():
        raise InvalidAuditEvent("target_id must not be empty")

    return AuditEvent.objects.create(
        actor=actor,
        action=action,
        target_model=target_model,
        target_id=target_id,
        metadata=_sanitize_metadata(metadata or {}),
        ip_address=ip_address,
        user_agent=user_agent,
    )
