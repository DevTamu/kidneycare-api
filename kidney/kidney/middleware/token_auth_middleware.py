# middleware/token_auth_middleware.py
import logging
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Log the entire query string for debugging
        query_string = scope.get("query_string", b"").decode()
        logger.debug(f"Raw query string: {query_string}")
        logger.info(f"Raw query string: {query_string}")
        
        query_params = parse_qs(query_string)
        logger.debug(f"Parsed query params: {query_params}")
        logger.info(f"Parsed query params: {query_params}")
        
        token_list = query_params.get("token", [None])
        token = token_list[0] if token_list else None
        logger.debug(f"Extracted token: {token}")
        logger.info(f"Extracted token: {token}")

        if not token:
            logger.error("No token provided in WebSocket connection")
            await send({"type": "websocket.close", "code": 4001})
            return

        try:
            user = await self.authenticate_token(token)
            if not user:
                logger.error(f"Invalid token: {token}")
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
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            return get_user_model().objects.get(id=user_id)
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return None