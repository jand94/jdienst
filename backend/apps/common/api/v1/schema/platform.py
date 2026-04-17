from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view

from apps.common.api.v1.serializers import (
    ApiErrorResponseSerializer,
    PlatformCheckResponseSerializer,
    PlatformHealthResponseSerializer,
    PlatformSloReportResponseSerializer,
)


platform_health_viewset_schema = extend_schema_view(
    snapshot=extend_schema(
        tags=["Common - Platform - Health"],
        summary="Returns platform health snapshot for audit/idempotency/outbox.",
        responses={200: PlatformHealthResponseSerializer, 403: ApiErrorResponseSerializer},
        parameters=[
            OpenApiParameter(
                name="window_hours",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Time window used for health aggregation.",
            )
        ],
    ),
)


platform_ops_viewset_schema = extend_schema_view(
    check=extend_schema(
        tags=["Common - Platform - Operations"],
        summary="Runs enterprise platform compliance checks.",
        responses={200: PlatformCheckResponseSerializer, 403: ApiErrorResponseSerializer},
    ),
    slo_report=extend_schema(
        tags=["Common - Platform - Operations"],
        summary="Generates a platform SLO report and applies maintenance tasks.",
        responses={200: PlatformSloReportResponseSerializer, 403: ApiErrorResponseSerializer},
    ),
    tenant_consistency=extend_schema(
        tags=["Common - Platform - Operations"],
        summary="Validates tenant membership consistency constraints.",
        responses={200: OpenApiTypes.OBJECT, 403: ApiErrorResponseSerializer},
    ),
    soft_delete_cleanup=extend_schema(
        tags=["Common - Platform - Operations"],
        summary="Runs soft-delete retention cleanup for technical records.",
        responses={200: OpenApiTypes.OBJECT, 403: ApiErrorResponseSerializer},
    ),
)
