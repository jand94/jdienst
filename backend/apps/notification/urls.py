from django.urls import include, path

urlpatterns = [
    path("v1/", include("apps.notification.api.v1.urls")),
]
