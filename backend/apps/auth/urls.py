from django.urls import include, path

urlpatterns = [
    path("v1/", include("apps.auth.api.v1.urls")),
]
