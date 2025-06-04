from django.urls import path
from .views import (
    GetNotificationChatsToProviderView,
    GetProvidersChatView,
    GetProviderChatInformationView,
    GetPatientsChatView,
    GetPatientChatInformationView
)

urlpatterns = [
    path("notifications/chats/", GetNotificationChatsToProviderView.as_view(), name='chat-messages'),
    path("providers/chats/", GetProvidersChatView.as_view(), name='providers-chat'),
    path("providers/<str:pk>/chat/messages/", GetProviderChatInformationView.as_view(), name='providers-pk-chat'),
    path("patients/chat/", GetPatientsChatView.as_view(), name='patients-chat'),
    path("patients/<str:pk>/chat/messages/", GetPatientChatInformationView.as_view(), name='patients-pk-chat'),
]
