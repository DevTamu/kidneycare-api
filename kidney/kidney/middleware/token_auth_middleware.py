# middleware/token_auth_middleware.py
import logging
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken

from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            # Extract token from query string
            query_string = scope.get("query_string", b"").decode()
            query_params = parse_qs(query_string)
            token = query_params.get("token", [None])[0]
            
            if not token:
                logger.warning("No token provided in WebSocket connection")
                await send({"type": "websocket.close", "code": 4001})
                return

            # Authenticate user
            user = await self.authenticate_token(token)
            if not user:
                logger.warning(f"Invalid token: {token}")
                await send({"type": "websocket.close", "code": 4003})
                return

            scope["user"] = user
            logger.info(f"Authenticated user: {user.id}")
            return await self.app(scope, receive, send)

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            await send({"type": "websocket.close", "code": 4003})

    @database_sync_to_async
    def authenticate_token(self, token):
        from django.contrib.auth import get_user_model
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            return get_user_model().objects.get(id=user_id)
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return None