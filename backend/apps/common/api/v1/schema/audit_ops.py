from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view

from apps.common.api.v1.serializers import (
    ApiErrorResponseSerializer,
    AuditArchiveRequestSerializer,
    AuditArchiveResponseSerializer,
    AuditHealthSnapshotResponseSerializer,
    AuditIntegrityVerifyRequestSerializer,
    AuditIntegrityVerifyResponseSerializer,
    AuditSetupRolesResponseSerializer,
    AuditSiemExportPreviewResponseSerializer,
)


audit_ops_viewset_schema = extend_schema_view(
    health_snapshot=extend_schema(
        tags=["Common - Audit Operations - Monitoring"],
        summary="Liefert Audit-Health-Snapshot",
        responses={200: AuditHealthSnapshotResponseSerializer, 403: ApiErrorResponseSerializer},
        parameters=[
            OpenApiParameter(
                name="window_hours",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Zeitfenster fuer Snapshot in Stunden (1-720).",
            ),
        ],
    ),
    verify_integrity=extend_schema(
        tags=["Common - Audit Operations - Integrity"],
        summary="Startet Integritaets-Verifikation und optionalen Checkpoint",
        request=AuditIntegrityVerifyRequestSerializer,
        responses={200: AuditIntegrityVerifyResponseSerializer, 400: ApiErrorResponseSerializer, 403: ApiErrorResponseSerializer},
    ),
    siem_export_preview=extend_schema(
        tags=["Common - Audit Operations - SIEM"],
        summary="Zeigt SIEM-Exportvorschau ohne Export-Markierung",
        responses={200: AuditSiemExportPreviewResponseSerializer, 400: ApiErrorResponseSerializer, 403: ApiErrorResponseSerializer},
        parameters=[
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Maximale Anzahl Vorschau-Events (1-500).",
            ),
        ],
    ),
    archive_events=extend_schema(
        tags=["Common - Audit Operations - Retention"],
        summary="Startet Audit-Archivierung (Tage-basiert oder Retention-Policy)",
        request=AuditArchiveRequestSerializer,
        responses={200: AuditArchiveResponseSerializer, 400: ApiErrorResponseSerializer, 403: ApiErrorResponseSerializer},
    ),
    setup_roles=extend_schema(
        tags=["Common - Audit Operations - Access"],
        summary="Synchronisiert konfigurierte Audit-Reader-Rollen",
        request=None,
        responses={200: AuditSetupRolesResponseSerializer, 403: ApiErrorResponseSerializer},
    ),
)
