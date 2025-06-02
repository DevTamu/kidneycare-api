from django.urls import path
from .views import (
    GetUsersMessageView,
    GetNotificationChatsToProviderView,
    GetProvidersChatView,
    GetPatientsChatView
)

urlpatterns = [
    path("chat/messages/<str:pk>/", GetUsersMessageView.as_view(), name='chat-messages'),
    path("notifications/chats/", GetNotificationChatsToProviderView.as_view(), name='chat-messages'),
    path("providers/chats/", GetProvidersChatView.as_view(), name='providers-chat'),
    path("patients/chat/", GetPatientsChatView.as_view(), name='patients-chat'),
    path("patients<str:pk>/chat/", GetPatientsChatView.as_view(), name='patients-chat'),
]
