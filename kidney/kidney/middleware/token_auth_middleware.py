from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken, TokenError


class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        
        try:

            token = self.get_token_from_scope(scope)

            if not token:
                print("[AUTH] No token provided, using AnonymousUser.")
                scope["user"] = AnonymousUser()
                return await self.inner(scope, receive, send)
                # raise TokenError("Authorization token not provided")

            user_id = await self.get_user_from_token(token)

            if not user_id:
                print("[AUTH] Invalid or expired token.")
                scope["user"] = AnonymousUser()
                return await self.inner(scope, receive, send)
                # raise TokenError("Invalid or expired token. Please log in again.")
            scope["user"] = await self.get_user(user_id) 

        except TokenError as e:
            print(f"[JWT ERROR] {str(e)}")
            await self.close_connection(send, code=4003)
            return
        except Exception as e:
            print(f"[UNEXPECTED ERROR] {str(e)}")
            await self.close_connection(send, code=4003)
            return
        
        return await self.inner(scope, receive, send)
    
    def get_token_from_scope(self, scope):
        #get the headers from the scope
        headers = dict(scope.get("headers", []))

        #get the authorization header
        auth_header = headers.get(b'authorization', b'').decode('utf-8')
        #if the authorization header exists and starts with 'Bearer ' return the token part
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]

    
    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            return access_token["user_id"]
        except TokenError as e:
            print(f"[TOKEN ERROR] {e}")
            return None
        except Exception as e:
            print(f"[TOKEN PARSE ERROR] {e}")
            return None
        
    @database_sync_to_async
    def get_user(self, user_id):
        from django.contrib.auth import get_user_model
        try:
            User = get_user_model()
            return User.objects.get(id=user_id)
        except Exception as e:
            print(f"[DB ERROR] Failed to fetch user {user_id}: {e}")
            return AnonymousUser()
        

    async def close_connection(self, send, code):
        await send({
            "type": "websocket.close",
            "code": code,
        })