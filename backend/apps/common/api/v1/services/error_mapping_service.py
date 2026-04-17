from __future__ import annotations

from typing import Any

from django.http import HttpRequest
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from apps.common.api.v1.services.audit_context_service import extract_audit_correlation_ids
from apps.common.exceptions import CommonError


def _build_error_payload(
    *,
    code: str,
    message: str,
    details: Any = None,
    request_id: str | None = None,
    trace_id: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": code,
        "message": message,
        "details": details or {},
    }
    payload["request_id"] = request_id
    payload["trace_id"] = trace_id
    return payload


def map_exception_to_response(
    exc: Exception,
    *,
    request: HttpRequest | None = None,
) -> tuple[int, dict[str, Any]]:
    request_id = None
    trace_id = None
    if request is not None:
        request_id, trace_id = extract_audit_correlation_ids(request)

    if isinstance(exc, CommonError):
        payload = _build_error_payload(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request_id,
            trace_id=trace_id,
        )
        return exc.status_code, payload

    if isinstance(exc, APIException):
        payload = _build_error_payload(
            code=getattr(exc, "default_code", "api_error"),
            message=str(exc.detail),
            request_id=request_id,
            trace_id=trace_id,
        )
        return exc.status_code, payload

    payload = _build_error_payload(
        code="internal_error",
        message="An internal error occurred.",
        request_id=request_id,
        trace_id=trace_id,
    )
    return status.HTTP_500_INTERNAL_SERVER_ERROR, payload


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    response = drf_exception_handler(exc, context)
    request = context.get("request")

    if response is None:
        status_code, payload = map_exception_to_response(exc, request=request)
        return Response({"error": payload}, status=status_code)

    status_code, payload = map_exception_to_response(exc, request=request)
    response.status_code = status_code
    response.data = {"error": payload}
    return response
