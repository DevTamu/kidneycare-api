from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken, TokenError


@database_sync_to_async
def get_user(user_id):
    from django.contrib.auth import get_user_model
    try:
        User = get_user_model()
        return User.objects.get(id=user_id)
    except Exception:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        
        token = self.get_token_from_scope(scope)

        if not token:
            raise TokenError("Authorization token not provided")

        user_id = await self.get_user_from_token(token)

        if not user_id:
            raise TokenError("Invalid or expired token. Please log in again.")

        scope["user"] = await get_user(user_id) 
        return await self.inner(scope, receive, send)
    
    def get_token_from_scope(self, scope):
        headers = dict(scope.get("headers", []))

        # 1. Try Authorization header
        auth_header = headers.get(b'authorization', b'').decode('utf-8')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            return access_token["user_id"]  
        except:
            return None