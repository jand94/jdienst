from rest_framework.routers import DefaultRouter

from apps.common.api.v1.views import (
    AuditEventViewSet,
    AuditOperationsViewSet,
    PlatformHealthViewSet,
    PlatformOperationsViewSet,
    TenantMembershipOperationsViewSet,
    TenantOperationsViewSet,
)

router = DefaultRouter()
router.register("audit-events", AuditEventViewSet, basename="common-audit-event")
router.register("audit-ops", AuditOperationsViewSet, basename="common-audit-ops")
router.register("platform-health", PlatformHealthViewSet, basename="common-platform-health")
router.register("platform-ops", PlatformOperationsViewSet, basename="common-platform-ops")
router.register("tenants", TenantOperationsViewSet, basename="common-tenant-ops")
router.register("tenant-memberships", TenantMembershipOperationsViewSet, basename="common-tenant-membership-ops")

urlpatterns = [
    *router.urls,
]
