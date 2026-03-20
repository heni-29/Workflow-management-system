# websockets/middleware.py
"""
JWT auth middleware for Django Channels WebSocket connections.

WebSockets can't send Authorization headers, so the client passes
the access token as a query parameter: ?token=<access_token>

This middleware decodes it and sets scope["user"] before the consumer runs.
"""
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model


@database_sync_to_async
def get_user_from_token(token_str):
    """Decode a JWT access token and return the matching User, or None."""
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken(token_str)
        User = get_user_model()
        return User.objects.get(id=token["user_id"])
    except Exception:
        return None


class JwtAuthMiddleware(BaseMiddleware):
    """Attach an authenticated user to the WebSocket scope via ?token=..."""

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token_list = params.get("token", [])

        if token_list:
            user = await get_user_from_token(token_list[0])
            scope["user"] = user or AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(inner)
