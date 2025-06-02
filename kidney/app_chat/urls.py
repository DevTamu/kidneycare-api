from django.urls import path
from .views import (
    GetUsersMessageView,
    GetNotificationChatsToProviderView,
    GetProvidersChatView,
    GetProviderChatInformationView,
    GetPatientsChatView,
    GetPatientChatInformationView
)

urlpatterns = [
    path("chat/messages/<str:pk>/", GetUsersMessageView.as_view(), name='chat-messages'),
    path("notifications/chats/", GetNotificationChatsToProviderView.as_view(), name='chat-messages'),
    path("providers/chats/", GetProvidersChatView.as_view(), name='providers-chat'),
    path("providers/<str:pk>/chats/", GetProviderChatInformationView.as_view(), name='providers-pk-chat'),
    path("patients/chat/", GetPatientsChatView.as_view(), name='patients-chat'),
    path("patients/<str:pk>/chat/", GetPatientChatInformationView.as_view(), name='patients-pk-chat'),
]
