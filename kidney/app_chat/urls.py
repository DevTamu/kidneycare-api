from django.urls import path
from .views import (
    GetNotificationChatsToProviderView,
    UpdateNotificationChatInProviderView,
    GetProvidersChatView,
    GetProviderChatInformationView,
    GetPatientsChatView,
    GetPatientChatInformationView
)

urlpatterns = [
    path("chat/notifications/", GetNotificationChatsToProviderView.as_view(), name='chat-notifications-list'),
    path("chat/<int:pk>/notifications/", UpdateNotificationChatInProviderView.as_view(), name='chat-notifications'),
    path("providers/chats/", GetProvidersChatView.as_view(), name='providers-chat'),
    path("providers/<str:pk>/chat/messages/", GetProviderChatInformationView.as_view(), name='providers-pk-chat'),
    path("patients/chat/", GetPatientsChatView.as_view(), name='patients-chat'),
    path("patients/<str:pk>/chat/messages/", GetPatientChatInformationView.as_view(), name='patients-pk-chat'),
]
