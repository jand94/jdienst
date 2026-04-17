from __future__ import annotations

import uuid

from apps.common.api.v1.services.audit_context_service import (
    clear_request_context,
    extract_audit_correlation_ids,
    set_request_context,
)
from apps.common.constants import HeaderName


class CommonRequestContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id, trace_id = extract_audit_correlation_ids(request)
        request_id = request_id or str(uuid.uuid4())
        trace_id = trace_id or request_id
        request.common_request_id = request_id
        request.common_trace_id = trace_id
        tenant = getattr(request, "common_tenant", None)
        set_request_context(
            {
                "request_id": request_id,
                "trace_id": trace_id,
                "path": request.path,
                "method": request.method,
                "user_id": str(getattr(getattr(request, "user", None), "pk", "")) or None,
                "tenant_id": str(getattr(tenant, "pk", "")) or None,
                "tenant_slug": getattr(tenant, "slug", None),
            }
        )
        response = self.get_response(request)
        response[HeaderName.REQUEST_ID.value] = request_id
        response[HeaderName.TRACE_ID.value] = trace_id
        clear_request_context()
        return response
