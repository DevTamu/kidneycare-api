# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/appointment/", consumers.AppointmentConsumer.as_asgi()),
    # re_path(r"ws/chat/(?P<room_name>[a-f0-9\-]{36})/$", consumers.ChatConsumer.as_asgi()),
]

