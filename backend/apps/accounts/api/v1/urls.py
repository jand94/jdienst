from rest_framework.routers import DefaultRouter

from apps.accounts.api.v1.views import AccountUserViewSet

router = DefaultRouter()
router.register("users", AccountUserViewSet, basename="accounts-user")

urlpatterns = [
    *router.urls,
]
