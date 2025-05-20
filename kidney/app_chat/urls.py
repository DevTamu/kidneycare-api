from django.urls import path
from .views import (
    GetUsersMessageView,
    GetNotificationChatsInProviderView
)

urlpatterns = [
    path("chat/messages/<str:pk>/", GetUsersMessageView.as_view(), name='chat-messages'),
    path("notifications/chats/<str:pk>/", GetNotificationChatsInProviderView.as_view(), name='chat-messages')
]
