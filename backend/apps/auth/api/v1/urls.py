from django.urls import path

from apps.auth.api.v1.views import AuthLoginView, AuthLogoutView, AuthRefreshView

urlpatterns = [
    path("login/", AuthLoginView.as_view(), name="auth-login"),
    path("refresh/", AuthRefreshView.as_view(), name="auth-refresh"),
    path("logout/", AuthLogoutView.as_view(), name="auth-logout"),
]
