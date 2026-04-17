from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.common.api.v1.permissions import IsAuditReader
from apps.common.api.v1.schema import audit_event_viewset_schema
from apps.common.api.v1.serializers import AuditEventSerializer
from apps.common.models import AuditEvent


class AuditEventPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 200
    page_size_query_param = "page_size"


@audit_event_viewset_schema
class AuditEventViewSet(ReadOnlyModelViewSet):
    serializer_class = AuditEventSerializer
    permission_classes = [IsAuditReader]
    queryset = AuditEvent.objects.select_related("actor").order_by("-created_at")
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["action", "target_model", "target_id", "actor"]
    ordering_fields = ["created_at", "action"]
    ordering = ["-created_at"]
    pagination_class = AuditEventPagination
