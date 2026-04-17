from django.urls import include, path

urlpatterns = [
    path("v1/", include("apps.common.api.v1.urls")),
]
