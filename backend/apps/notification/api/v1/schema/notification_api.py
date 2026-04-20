from __future__ import annotations

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema, extend_schema_view

from apps.common.api.v1.serializers import ApiErrorResponseSerializer
from apps.notification.api.v1.serializers import (
    NotificationBulkMarkReadSerializer,
    NotificationCreateSerializer,
    NotificationPreferenceReadSerializer,
    NotificationPreferenceUpdateSerializer,
    NotificationReadSerializer,
)


notification_viewset_schema = extend_schema_view(
    list=extend_schema(
        operation_id="notification_v1_notifications_list",
        tags=["Notification - Inbox"],
        summary="List authenticated user's notifications",
        responses={
            200: OpenApiResponse(response=NotificationReadSerializer(many=True)),
            401: OpenApiResponse(response=ApiErrorResponseSerializer),
            403: OpenApiResponse(response=ApiErrorResponseSerializer),
        },
        parameters=[
            OpenApiParameter(
                name="include_archived",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Include archived notifications when true.",
            ),
            OpenApiParameter(
                name="X-Tenant-Slug",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
                description="Tenant scope for notification queries.",
            ),
        ],
    ),
    create=extend_schema(
        operation_id="notification_v1_notifications_create",
        tags=["Notification - Delivery"],
        summary="Create a notification for a recipient",
        request=NotificationCreateSerializer,
        responses={
            201: OpenApiResponse(response=NotificationReadSerializer),
            400: OpenApiResponse(response=ApiErrorResponseSerializer),
            401: OpenApiResponse(response=ApiErrorResponseSerializer),
            403: OpenApiResponse(response=ApiErrorResponseSerializer),
            404: OpenApiResponse(response=ApiErrorResponseSerializer),
            429: OpenApiResponse(response=ApiErrorResponseSerializer),
        },
    ),
)


notification_mark_read_schema = extend_schema(
    operation_id="notification_v1_notifications_mark_read_create",
    tags=["Notification - Inbox - State"],
    summary="Mark one notification as read",
    request=None,
    responses={
        200: OpenApiResponse(response=NotificationReadSerializer),
        401: OpenApiResponse(response=ApiErrorResponseSerializer),
        403: OpenApiResponse(response=ApiErrorResponseSerializer),
        404: OpenApiResponse(response=ApiErrorResponseSerializer),
        429: OpenApiResponse(response=ApiErrorResponseSerializer),
    },
)


notification_bulk_mark_read_schema = extend_schema(
    operation_id="notification_v1_notifications_bulk_mark_read_create",
    tags=["Notification - Inbox - State"],
    summary="Mark multiple notifications as read",
    request=NotificationBulkMarkReadSerializer,
    responses={
        200: OpenApiResponse(
            description="Bulk mark-read result payload.",
        ),
        400: OpenApiResponse(response=ApiErrorResponseSerializer),
        401: OpenApiResponse(response=ApiErrorResponseSerializer),
        403: OpenApiResponse(response=ApiErrorResponseSerializer),
        429: OpenApiResponse(response=ApiErrorResponseSerializer),
    },
)


notification_preference_viewset_schema = extend_schema_view(
    list=extend_schema(
        operation_id="notification_v1_preferences_list",
        tags=["Notification - Preferences"],
        summary="List effective user notification preferences",
        responses={
            200: OpenApiResponse(response=NotificationPreferenceReadSerializer(many=True)),
            401: OpenApiResponse(response=ApiErrorResponseSerializer),
            403: OpenApiResponse(response=ApiErrorResponseSerializer),
        },
    ),
    create=extend_schema(
        operation_id="notification_v1_preferences_create",
        tags=["Notification - Preferences"],
        summary="Subscribe or unsubscribe a notification channel",
        request=NotificationPreferenceUpdateSerializer,
        responses={
            201: OpenApiResponse(response=NotificationPreferenceReadSerializer),
            400: OpenApiResponse(response=ApiErrorResponseSerializer),
            401: OpenApiResponse(response=ApiErrorResponseSerializer),
            403: OpenApiResponse(response=ApiErrorResponseSerializer),
            404: OpenApiResponse(response=ApiErrorResponseSerializer),
            429: OpenApiResponse(response=ApiErrorResponseSerializer),
        },
    ),
)


notification_ops_snapshot_schema = extend_schema(
    operation_id="notification_v1_ops_health_snapshot",
    tags=["Notification - Operations - Health"],
    summary="Return notification delivery health and SLO snapshot",
    parameters=[
        OpenApiParameter(
            name="window_hours",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Observation window for success/failure rate calculations.",
        ),
        OpenApiParameter(
            name="X-Tenant-Slug",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=False,
            description="Optional tenant context for operator auditing.",
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="Notification pipeline snapshot including pending backlog and failure counts.",
        ),
        401: OpenApiResponse(response=ApiErrorResponseSerializer),
        403: OpenApiResponse(response=ApiErrorResponseSerializer),
        429: OpenApiResponse(response=ApiErrorResponseSerializer),
    },
)
