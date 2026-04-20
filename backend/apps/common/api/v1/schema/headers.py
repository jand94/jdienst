from __future__ import annotations

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

from apps.common.constants import HeaderName


def tenant_slug_header_parameter(*, required: bool = True, description: str | None = None) -> OpenApiParameter:
    return OpenApiParameter(
        name=HeaderName.TENANT_SLUG.value,
        type=OpenApiTypes.STR,
        location=OpenApiParameter.HEADER,
        required=required,
        description=description or "Active tenant scope for the request.",
    )


def idempotency_key_header_parameter(
    *,
    required: bool = True,
    description: str | None = None,
) -> OpenApiParameter:
    return OpenApiParameter(
        name=HeaderName.IDEMPOTENCY_KEY.value,
        type=OpenApiTypes.STR,
        location=OpenApiParameter.HEADER,
        required=required,
        description=description or "Idempotency key for mutation safety.",
    )


def request_id_header_parameter(*, required: bool = False, description: str | None = None) -> OpenApiParameter:
    return OpenApiParameter(
        name=HeaderName.REQUEST_ID.value,
        type=OpenApiTypes.STR,
        location=OpenApiParameter.HEADER,
        required=required,
        description=description or "Optional request correlation identifier.",
    )


def trace_id_header_parameter(*, required: bool = False, description: str | None = None) -> OpenApiParameter:
    return OpenApiParameter(
        name=HeaderName.TRACE_ID.value,
        type=OpenApiTypes.STR,
        location=OpenApiParameter.HEADER,
        required=required,
        description=description or "Optional trace correlation identifier.",
    )
