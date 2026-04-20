from __future__ import annotations

import logging
from typing import Any

LOGGER = logging.getLogger("apps.notification.pipeline")

_SENSITIVE_KEYS = {
    "password",
    "secret",
    "token",
    "authorization",
    "api_key",
    "access_token",
    "refresh_token",
}


def sanitize_for_log(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if key.lower() in _SENSITIVE_KEYS:
                continue
            sanitized[key] = sanitize_for_log(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_for_log(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def log_pipeline_event(
    *,
    event: str,
    level: int = logging.INFO,
    request_id: str | None = None,
    trace_id: str | None = None,
    **payload: Any,
) -> None:
    sanitized_payload = sanitize_for_log(payload)
    LOGGER.log(
        level,
        event,
        extra={
            "event": event,
            "request_id": request_id,
            "trace_id": trace_id,
            "payload": sanitized_payload,
        },
    )
