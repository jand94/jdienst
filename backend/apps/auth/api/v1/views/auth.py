from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.auth.api.v1.permissions import IsAuthenticatedForAuthMutation
from apps.auth.api.v1.schema import auth_login_schema, auth_logout_schema, auth_refresh_schema
from apps.auth.api.v1.serializers import (
    AuthLoginRequestSerializer,
    AuthLogoutResponseSerializer,
    AuthNoopSerializer,
    AuthTokenSerializer,
)
from apps.auth.api.v1.services import login_with_credentials, logout_with_refresh_token, refresh_tokens
from apps.common.api.v1.services import extract_audit_correlation_ids


def _set_refresh_cookie(response: Response, *, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=settings.AUTH_REFRESH_COOKIE_MAX_AGE_SECONDS,
        httponly=settings.AUTH_REFRESH_COOKIE_HTTPONLY,
        secure=settings.AUTH_REFRESH_COOKIE_SECURE,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
        domain=settings.AUTH_REFRESH_COOKIE_DOMAIN,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        domain=settings.AUTH_REFRESH_COOKIE_DOMAIN,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
    )


def _extract_request_security_context(request) -> tuple[str | None, str]:
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip() or None
    else:
        ip_address = request.META.get("REMOTE_ADDR")
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    return ip_address, user_agent


class AuthLoginView(GenericAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"
    serializer_class = AuthLoginRequestSerializer

    @auth_login_schema
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request_id, trace_id = extract_audit_correlation_ids(request)
        ip_address, user_agent = _extract_request_security_context(request)
        tokens = login_with_credentials(
            identifier=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
            request_id=request_id,
            trace_id=trace_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        payload = AuthTokenSerializer({"access": tokens.access, "token_type": "Bearer"}).data
        response = Response(payload, status=status.HTTP_200_OK)
        _set_refresh_cookie(response, refresh_token=tokens.refresh)
        return response


class AuthRefreshView(GenericAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_refresh"
    serializer_class = AuthNoopSerializer

    @auth_refresh_schema
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
        if not refresh_token:
            raise AuthenticationFailed("Refresh token is missing.")

        request_id, trace_id = extract_audit_correlation_ids(request)
        ip_address, user_agent = _extract_request_security_context(request)
        tokens = refresh_tokens(
            refresh_token=refresh_token,
            request_id=request_id,
            trace_id=trace_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        payload = AuthTokenSerializer({"access": tokens.access, "token_type": "Bearer"}).data
        response = Response(payload, status=status.HTTP_200_OK)
        _set_refresh_cookie(response, refresh_token=tokens.refresh)
        return response


class AuthLogoutView(GenericAPIView):
    permission_classes = [IsAuthenticatedForAuthMutation]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_logout"
    serializer_class = AuthNoopSerializer

    @auth_logout_schema
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
        request_id, trace_id = extract_audit_correlation_ids(request)
        ip_address, user_agent = _extract_request_security_context(request)
        if refresh_token:
            logout_with_refresh_token(
                refresh_token=refresh_token,
                actor=request.user,
                request_id=request_id,
                trace_id=trace_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        payload = AuthLogoutResponseSerializer({"detail": "Logout successful."}).data
        response = Response(payload, status=status.HTTP_200_OK)
        _clear_refresh_cookie(response)
        return response
