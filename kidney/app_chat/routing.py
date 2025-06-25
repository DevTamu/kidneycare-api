# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<chat_type>nurse|head_nurse|admin|patient)/(?P<room_name>[a-f0-9\-]{36})/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/chat/inbox/$", consumers.InboxConsumer.as_asgi()),
]

