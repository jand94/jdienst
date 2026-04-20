from __future__ import annotations

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def _resolve_user_from_token(token: str):
    try:
        payload = AccessToken(token)
        user_id = payload.get("user_id")
        if user_id is None:
            return AnonymousUser()
        return User.objects.filter(pk=user_id).first() or AnonymousUser()
    except Exception:  # noqa: BLE001
        return AnonymousUser()


class NotificationJwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        user = scope.get("user")
        if not getattr(user, "is_authenticated", False):
            query_string = scope.get("query_string", b"").decode("utf-8")
            params = parse_qs(query_string)
            token = params.get("token", [None])[0]
            if token:
                scope["user"] = await _resolve_user_from_token(token)
        return await super().__call__(scope, receive, send)
