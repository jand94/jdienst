from __future__ import annotations

from apps.common.api.v1.services.tenant_context_service import (
    clear_tenant_context,
    resolve_request_tenant,
    set_tenant_context,
)


class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = resolve_request_tenant(request)
        request.common_tenant = tenant
        set_tenant_context(
            {
                "tenant_id": str(tenant.pk) if tenant else None,
                "tenant_slug": tenant.slug if tenant else None,
            }
        )
        response = self.get_response(request)
        clear_tenant_context()
        return response
