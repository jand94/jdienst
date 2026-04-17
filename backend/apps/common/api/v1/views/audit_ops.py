from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.common.api.v1.permissions import IsAuditOperator
from apps.common.api.v1.schema import audit_ops_viewset_schema
from apps.common.api.v1.serializers import (
    AuditArchiveRequestSerializer,
    AuditHealthSnapshotQuerySerializer,
    AuditIntegrityVerifyRequestSerializer,
    AuditSiemExportPreviewQuerySerializer,
)
from apps.common.api.v1.services import (
    archive_events_by_retention_policy,
    archive_old_events,
    collect_audit_health_snapshot,
    ensure_audit_reader_roles,
    export_events_for_siem,
    verify_integrity_chain,
)


@audit_ops_viewset_schema
class AuditOperationsViewSet(GenericViewSet):
    permission_classes = [IsAuditOperator]

    @action(detail=False, methods=["get"], url_path="health-snapshot")
    def health_snapshot(self, request):
        serializer = AuditHealthSnapshotQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        payload = collect_audit_health_snapshot(
            window_hours=serializer.validated_data.get("window_hours", 24),
        )
        return Response(payload)

    @action(detail=False, methods=["post"], url_path="verify-integrity")
    def verify_integrity(self, request):
        serializer = AuditIntegrityVerifyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verification = verify_integrity_chain(
            limit=serializer.validated_data.get("limit"),
            create_checkpoint=serializer.validated_data.get("create_checkpoint", False),
            source="api",
        )
        return Response(
            {
                "id": str(verification.pk),
                "status": verification.status,
                "checked_events": verification.checked_events,
                "last_event_hash": verification.last_event_hash,
                "details": verification.details,
                "checkpoint_id": str(verification.checkpoint_id) if verification.checkpoint_id else None,
            }
        )

    @action(detail=False, methods=["get"], url_path="siem-export-preview")
    def siem_export_preview(self, request):
        serializer = AuditSiemExportPreviewQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        payloads, failures, event_ids = export_events_for_siem(
            limit=serializer.validated_data.get("limit", 100),
        )
        return Response(
            {
                "exportable_count": len(payloads),
                "failure_count": len(failures),
                "event_ids": event_ids,
                "preview": payloads,
                "failures": failures,
            }
        )

    @action(detail=False, methods=["post"], url_path="archive-events")
    def archive_events(self, request):
        serializer = AuditArchiveRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get("use_retention_policy", False):
            affected = archive_events_by_retention_policy()
            mode = "retention_policy"
        else:
            affected = archive_old_events(before_days=serializer.validated_data.get("before_days", 90))
            mode = "before_days"
        return Response({"archived_events": affected, "mode": mode}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="setup-roles")
    def setup_roles(self, request):
        role_names, created_total = ensure_audit_reader_roles()
        return Response(
            {
                "roles": role_names,
                "created_roles": created_total,
            },
            status=status.HTTP_200_OK,
        )
