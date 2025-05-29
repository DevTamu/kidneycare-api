# middleware/token_auth_middleware.py
import logging
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        try:
            # 1. Extract token from query parameters
            query_string = scope.get("query_string", b"").decode()
            logger.debug(f"Raw query string: {query_string}")
            
            query_params = parse_qs(query_string)
            token = query_params.get("token", [None])[0]
            logger.debug(f"Extracted token: {token}")

            if not token:
                logger.error("No token provided in WebSocket connection")
                await send({"type": "websocket.close", "code": 4001})
                return

            # 2. Authenticate user
            user = await self.authenticate_token(token)
            if not user:
                logger.error("Invalid or expired token")
                await send({"type": "websocket.close", "code": 4003})
                return

            # 3. Add user to scope
            scope["user"] = user
            logger.info(f"Authenticated user: {user.id}")
            
            # 4. Proceed to consumer
            return await self.inner(scope, receive, send)

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}", exc_info=True)
            await send({"type": "websocket.close", "code": 4003})

    @database_sync_to_async
    def authenticate_token(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            return get_user_model().objects.get(id=user_id)
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return None