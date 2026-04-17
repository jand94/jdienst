from django.conf import settings
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema

from apps.auth.api.v1.serializers import (
    AuthErrorEnvelopeSerializer,
    AuthLoginRequestSerializer,
    AuthLogoutResponseSerializer,
    AuthTokenSerializer,
)


auth_login_schema = extend_schema(
    tags=["Auth - Session"],
    operation_id="auth_v1_login_create",
    summary="Authenticate with username or email and issue JWT token pair",
    request=AuthLoginRequestSerializer,
    responses={
        200: OpenApiResponse(response=AuthTokenSerializer),
        401: OpenApiResponse(response=AuthErrorEnvelopeSerializer, description="Invalid credentials."),
    },
    auth=[],
)

auth_refresh_schema = extend_schema(
    tags=["Auth - Session"],
    operation_id="auth_v1_refresh_create",
    summary="Rotate refresh token cookie and issue new access token",
    parameters=[
        OpenApiParameter(
            name=settings.AUTH_REFRESH_COOKIE_NAME,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.COOKIE,
            required=True,
            description="HttpOnly refresh token cookie.",
        )
    ],
    responses={
        200: OpenApiResponse(response=AuthTokenSerializer),
        401: OpenApiResponse(response=AuthErrorEnvelopeSerializer, description="Refresh token is invalid."),
    },
    auth=[],
)

auth_logout_schema = extend_schema(
    tags=["Auth - Session"],
    operation_id="auth_v1_logout_create",
    summary="Revoke active refresh token and clear cookie",
    parameters=[
        OpenApiParameter(
            name=settings.AUTH_REFRESH_COOKIE_NAME,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.COOKIE,
            required=False,
            description="HttpOnly refresh token cookie to revoke.",
        )
    ],
    responses={
        200: OpenApiResponse(response=AuthLogoutResponseSerializer, description="Logout completed."),
        401: OpenApiResponse(response=AuthErrorEnvelopeSerializer, description="Authentication failed."),
    },
    auth=["BearerAuth"],
)
