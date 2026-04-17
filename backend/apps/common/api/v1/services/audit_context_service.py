from __future__ import annotations

from typing import Any

_REQUEST_ID_HEADERS = ("X-Request-ID", "X-Correlation-ID")
_TRACE_ID_HEADERS = ("X-Trace-ID", "traceparent")


def _first_header_value(headers: Any, candidates: tuple[str, ...]) -> str | None:
    for header in candidates:
        value = headers.get(header)
        if isinstance(value, str):
            normalized = value.strip()
            if normalized:
                return normalized
    return None


def extract_audit_correlation_ids(request) -> tuple[str | None, str | None]:
    headers = getattr(request, "headers", {})
    request_id = _first_header_value(headers, _REQUEST_ID_HEADERS)
    trace_id = _first_header_value(headers, _TRACE_ID_HEADERS)
    return request_id, trace_id
