from rest_framework.routers import DefaultRouter

from apps.common.api.v1.views import AuditEventViewSet, AuditOperationsViewSet

router = DefaultRouter()
router.register("audit-events", AuditEventViewSet, basename="common-audit-event")
router.register("audit-ops", AuditOperationsViewSet, basename="common-audit-ops")

urlpatterns = [
    *router.urls,
]
