from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from apps.common.api.v1.services import record_audit_event


@dataclass(frozen=True)
class AuthTokens:
    access: str
    refresh: str


def _get_user_by_identifier(*, identifier: str):
    normalized = identifier.strip()
    if not normalized:
        return None
    User = get_user_model()
    return User.objects.filter(
        Q(username__iexact=normalized) | Q(email__iexact=normalized)
    ).first()


def _issue_tokens_for_user(*, user) -> AuthTokens:
    refresh = RefreshToken.for_user(user)
    return AuthTokens(access=str(refresh.access_token), refresh=str(refresh))


def _record_auth_event(
    *,
    action: str,
    actor,
    target_id: str,
    metadata: dict | None,
    request_id: str | None,
    trace_id: str | None,
    ip_address: str | None = None,
    user_agent: str = "",
):
    return record_audit_event(
        action=action,
        target_model="accounts.User",
        target_id=target_id,
        actor=actor,
        metadata={"source": "api", **(metadata or {})},
        request_id=request_id,
        trace_id=trace_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


def login_with_credentials(
    *,
    identifier: str,
    password: str,
    request_id: str | None = None,
    trace_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str = "",
) -> AuthTokens:
    user = _get_user_by_identifier(identifier=identifier)
    if user is None or not check_password(password, user.password):
        target_id = str(getattr(user, "pk", "unknown"))
        _record_auth_event(
            action="auth.login.failed",
            actor=None,
            target_id=target_id,
            metadata={"reason": "invalid_credentials"},
            request_id=request_id,
            trace_id=trace_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        raise AuthenticationFailed("Invalid username or password.")
    if not user.is_active:
        _record_auth_event(
            action="auth.login.failed",
            actor=user,
            target_id=str(user.pk),
            metadata={"reason": "inactive_user"},
            request_id=request_id,
            trace_id=trace_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        raise AuthenticationFailed("User account is inactive.")

    tokens = _issue_tokens_for_user(user=user)
    _record_auth_event(
        action="auth.login.succeeded",
        actor=user,
        target_id=str(user.pk),
        metadata={"result": "succeeded"},
        request_id=request_id,
        trace_id=trace_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return tokens


def refresh_tokens(
    *,
    refresh_token: str,
    request_id: str | None = None,
    trace_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str = "",
) -> AuthTokens:
    serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
    try:
        serializer.is_valid(raise_exception=True)
    except (ValidationError, TokenError) as exc:
        _record_auth_event(
            action="auth.refresh.failed",
            actor=None,
            target_id="unknown",
            metadata={"reason": "invalid_refresh_token"},
            request_id=request_id,
            trace_id=trace_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        raise AuthenticationFailed("Refresh token is invalid.") from exc

    refreshed = serializer.validated_data
    new_refresh = refreshed.get("refresh")
    if not new_refresh:
        new_refresh = refresh_token

    try:
        token = RefreshToken(new_refresh)
    except TokenError as exc:
        raise AuthenticationFailed("Refresh token is invalid.") from exc

    user_id = str(token.get("user_id", "unknown"))
    _record_auth_event(
        action="auth.refresh.succeeded",
        actor=None,
        target_id=user_id,
        metadata={"result": "succeeded"},
        request_id=request_id,
        trace_id=trace_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return AuthTokens(access=refreshed["access"], refresh=new_refresh)


def logout_with_refresh_token(
    *,
    refresh_token: str,
    actor,
    request_id: str | None = None,
    trace_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str = "",
) -> None:
    try:
        token = RefreshToken(refresh_token)
        token_user_id = str(token.get("user_id", ""))
        actor_id = str(getattr(actor, "pk", ""))
        if token_user_id != actor_id:
            _record_auth_event(
                action="auth.logout.failed",
                actor=actor,
                target_id=actor_id or "unknown",
                metadata={"reason": "token_user_mismatch"},
                request_id=request_id,
                trace_id=trace_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise AuthenticationFailed("Refresh token does not belong to authenticated user.")
        token.blacklist()
    except TokenError as exc:
        _record_auth_event(
            action="auth.logout.failed",
            actor=actor,
            target_id=str(getattr(actor, "pk", "unknown")),
            metadata={"reason": "invalid_refresh_token"},
            request_id=request_id,
            trace_id=trace_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        raise AuthenticationFailed("Refresh token is invalid.") from exc

    _record_auth_event(
        action="auth.logout.succeeded",
        actor=actor,
        target_id=str(getattr(actor, "pk", "unknown")),
        metadata={"result": "succeeded"},
        request_id=request_id,
        trace_id=trace_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
