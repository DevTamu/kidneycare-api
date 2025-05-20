import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kidney.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from .routing import websocket_urlpatterns
from .middleware.token_auth_middleware import JWTAuthMiddleware  

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        )
    }
)
