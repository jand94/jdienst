from rest_framework.routers import DefaultRouter

from apps.common.api.v1.views import AuditEventViewSet

router = DefaultRouter()
router.register("audit-events", AuditEventViewSet, basename="common-audit-event")

urlpatterns = [
    *router.urls,
]
