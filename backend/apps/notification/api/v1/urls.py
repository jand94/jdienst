from rest_framework.routers import DefaultRouter

from apps.notification.api.v1.views import NotificationPreferenceViewSet, NotificationViewSet

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="notification")
router.register("preferences", NotificationPreferenceViewSet, basename="notification-preference")

urlpatterns = [
    *router.urls,
]
