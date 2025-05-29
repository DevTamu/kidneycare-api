# routing.py
from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from . import consumers
from .middleware.token_auth_middleware import JWTAuthMiddleware

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>[a-f0-9]{32})/$", consumers.ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})