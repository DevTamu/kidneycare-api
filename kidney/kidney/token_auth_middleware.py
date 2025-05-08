from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()

@database_sync_to_async
def get_user(token):
    try:
        access_token = AccessToken(token)
        user = User.objects.get(id=access_token["user_id"])
        return user
    except Exception:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        token = parse_qs(query_string).get("token", [None])[0]

        scope["user"] = await get_user(token)

        return await self.inner(scope, receive, send)
