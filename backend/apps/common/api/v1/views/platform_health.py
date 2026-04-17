from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.common.api.v1.permissions import IsAuditOperator
from apps.common.api.v1.schema import platform_health_viewset_schema
from apps.common.api.v1.serializers import PlatformHealthQuerySerializer
from apps.common.api.v1.services import collect_platform_health_snapshot


@platform_health_viewset_schema
class PlatformHealthViewSet(GenericViewSet):
    permission_classes = [IsAuditOperator]
    serializer_class = PlatformHealthQuerySerializer

    @action(detail=False, methods=["get"], url_path="snapshot")
    def snapshot(self, request):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        payload = collect_platform_health_snapshot(
            window_hours=serializer.validated_data.get("window_hours", 24),
        )
        return Response(payload)
