from django.urls import path
from .views import (
    GetUsersMessageView,
    GetNotificationChatsToProviderView,
    GetUsersChatView,
    GetProvidersChatView
)

urlpatterns = [
    path("chat/messages/<str:pk>/", GetUsersMessageView.as_view(), name='chat-messages'),
    path("notifications/chats/", GetNotificationChatsToProviderView.as_view(), name='chat-messages'),
    path("get/users/chats/", GetUsersChatView.as_view(), name='get-users-chats'),
    path("providers/chats/", GetProvidersChatView.as_view(), name='providers-chat')
]
