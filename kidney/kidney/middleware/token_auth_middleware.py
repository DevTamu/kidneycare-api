# middleware/token_auth_middleware.py
import logging
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token_list = query_params.get("token")
        token = token_list[0] if token_list else None

        if not token:
            logger.warning("No token provided in WebSocket connection")
            await send({"type": "websocket.close", "code": 4001})
            return

        try:
            access_token = AccessToken(token)
            user = await self.get_user(access_token["user_id"])
            if not user:
                logger.warning(f"User not found for token: {token}")
                await send({"type": "websocket.close", "code": 4003})
                return

            scope["user"] = user
            logger.info(f"Authenticated user: {user.id}")
        except TokenError as e:
            logger.warning(f"Token error: {str(e)}")
            await send({"type": "websocket.close", "code": 4003})
            return

        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        return get_user_model().objects.get(id=user_id)