from __future__ import annotations

from contextvars import ContextVar
from typing import Any

from apps.common.constants import HeaderName

_REQUEST_ID_HEADERS = (HeaderName.REQUEST_ID, HeaderName.CORRELATION_ID)
_TRACE_ID_HEADERS = (HeaderName.TRACE_ID, HeaderName.TRACE_PARENT)
_REQUEST_CONTEXT: ContextVar[dict[str, Any]] = ContextVar("common_request_context", default={})


def _first_header_value(headers: Any, candidates: tuple[str, ...]) -> str | None:
    for header in candidates:
        value = headers.get(header)
        if isinstance(value, str):
            normalized = value.strip()
            if normalized:
                return normalized
    return None


def extract_audit_correlation_ids(request) -> tuple[str | None, str | None]:
    request_id = getattr(request, "common_request_id", None)
    trace_id = getattr(request, "common_trace_id", None)
    if request_id or trace_id:
        return request_id, trace_id

    headers = getattr(request, "headers", {})
    request_id = _first_header_value(headers, _REQUEST_ID_HEADERS)
    trace_id = _first_header_value(headers, _TRACE_ID_HEADERS)
    return request_id, trace_id


def set_request_context(context: dict[str, Any]) -> None:
    _REQUEST_CONTEXT.set(context)


def get_request_context() -> dict[str, Any]:
    return dict(_REQUEST_CONTEXT.get())


def clear_request_context() -> None:
    _REQUEST_CONTEXT.set({})
