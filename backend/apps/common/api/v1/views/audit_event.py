from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.common.api.v1.pagination import DefaultListPagination
from apps.common.api.v1.permissions import IsAuditReader
from apps.common.api.v1.services import extract_audit_correlation_ids, log_audit_reader_access
from apps.common.api.v1.schema import audit_event_viewset_schema
from apps.common.api.v1.serializers import AuditEventSerializer
from apps.common.models import AuditEvent


@audit_event_viewset_schema
class AuditEventViewSet(ReadOnlyModelViewSet):
    serializer_class = AuditEventSerializer
    permission_classes = [IsAuditReader]
    queryset = AuditEvent.objects.select_related("actor").order_by("-created_at")
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["action", "target_model", "target_id", "actor"]
    ordering_fields = ["created_at", "action"]
    ordering = ["-created_at"]
    pagination_class = DefaultListPagination

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        request_id, trace_id = extract_audit_correlation_ids(request)
        log_audit_reader_access(
            actor=request.user,
            access_type="list",
            target_id="collection",
            source="api",
            request_id=request_id,
            trace_id=trace_id,
            metadata={
                "filters": {
                    key: request.query_params.get(key)
                    for key in ("action", "target_model", "target_id", "ordering")
                    if request.query_params.get(key)
                }
            },
        )
        return response

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().retrieve(request, *args, **kwargs)
        request_id, trace_id = extract_audit_correlation_ids(request)
        log_audit_reader_access(
            actor=request.user,
            access_type="retrieve",
            target_id=str(instance.pk),
            source="api",
            request_id=request_id,
            trace_id=trace_id,
        )
        return response
