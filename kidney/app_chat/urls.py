from django.urls import path
from .views import (
    GetUsersMessageView,
    GetNotificationChatsToProviderView
)

urlpatterns = [
    path("chat/messages/<str:pk>/", GetUsersMessageView.as_view(), name='chat-messages'),
    path("notifications/chats/", GetNotificationChatsToProviderView.as_view(), name='chat-messages')
]
