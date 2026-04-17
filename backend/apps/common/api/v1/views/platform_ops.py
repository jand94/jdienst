from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.common.api.v1.permissions import IsAuditOperator
from apps.common.api.v1.schema import platform_ops_viewset_schema
from apps.common.api.v1.serializers import PlatformOperationNoInputSerializer, PlatformSoftDeleteCleanupRequestSerializer
from apps.common.api.v1.services import (
    cleanup_soft_deleted_tenants,
    collect_tenant_consistency_snapshot,
    run_platform_check,
    run_platform_slo_report,
)


@platform_ops_viewset_schema
class PlatformOperationsViewSet(GenericViewSet):
    permission_classes = [IsAuditOperator]
    serializer_class = PlatformOperationNoInputSerializer

    @action(detail=False, methods=["post"], url_path="check")
    def check(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = run_platform_check(window_hours=serializer.validated_data.get("window_hours", 24))
        return Response(payload)

    @action(detail=False, methods=["post"], url_path="slo-report")
    def slo_report(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = run_platform_slo_report(window_hours=serializer.validated_data.get("window_hours", 24))
        return Response(payload)

    @action(detail=False, methods=["post"], url_path="tenant-consistency")
    def tenant_consistency(self, request):
        payload = collect_tenant_consistency_snapshot()
        return Response(payload)

    @action(detail=False, methods=["post"], url_path="soft-delete-cleanup")
    def soft_delete_cleanup(self, request):
        serializer = PlatformSoftDeleteCleanupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cleaned = cleanup_soft_deleted_tenants(
            older_than_days=serializer.validated_data.get("older_than_days", 30)
        )
        return Response({"cleaned_records": cleaned})
