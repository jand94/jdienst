from rest_framework.routers import DefaultRouter

from apps.fetests.api.v1.views import TaskViewSet

router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="fetests-task")

urlpatterns = [
    *router.urls,
]
