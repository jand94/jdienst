from rest_framework.routers import DefaultRouter

from apps.common.api.v1.views import (
    AuditEventViewSet,
    AuditOperationsViewSet,
    PlatformHealthViewSet,
    PlatformOperationsViewSet,
)

router = DefaultRouter()
router.register("audit-events", AuditEventViewSet, basename="common-audit-event")
router.register("audit-ops", AuditOperationsViewSet, basename="common-audit-ops")
router.register("platform-health", PlatformHealthViewSet, basename="common-platform-health")
router.register("platform-ops", PlatformOperationsViewSet, basename="common-platform-ops")

urlpatterns = [
    *router.urls,
]
