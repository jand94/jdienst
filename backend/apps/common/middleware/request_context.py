from __future__ import annotations

import uuid

from apps.common.api.v1.services.audit_context_service import (
    clear_request_context,
    extract_audit_correlation_ids,
    set_request_context,
)


class CommonRequestContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id, trace_id = extract_audit_correlation_ids(request)
        request_id = request_id or str(uuid.uuid4())
        trace_id = trace_id or request_id
        request.common_request_id = request_id
        request.common_trace_id = trace_id
        set_request_context(
            {
                "request_id": request_id,
                "trace_id": trace_id,
                "path": request.path,
                "method": request.method,
                "user_id": str(getattr(getattr(request, "user", None), "pk", "")) or None,
            }
        )
        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        response["X-Trace-ID"] = trace_id
        clear_request_context()
        return response
