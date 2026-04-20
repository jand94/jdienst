from django.urls import include, path

urlpatterns = [
    path("v1/", include("apps.fetests.api.v1.urls")),
]
