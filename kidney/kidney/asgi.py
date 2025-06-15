import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kidney.settings')
django.setup()
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from app_chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from app_appointment.routing import websocket_urlpatterns as appointment_websocket_urlpatterns
from .middleware.token_auth_middleware import JWTAuthMiddleware

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": JWTAuthMiddleware(
#         AuthMiddlewareStack(
#             URLRouter(websocket_urlpatterns)
#         )
#     )
# })

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            AuthMiddlewareStack(
                URLRouter(chat_websocket_urlpatterns + appointment_websocket_urlpatterns)
            )
        )
    )
})