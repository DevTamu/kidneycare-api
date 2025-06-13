from django.urls import path
from .views import (
    GetNotificationChatsToProviderView,
    UpdateNotificationChatInProviderView,
    GetProvidersChatView,
    # UpdateChatStatusInPatientView,
    GetProviderChatInformationView,
    GetPatientsChatView,
    GetPatientChatInformationView,
    SingleToSingleChatHistoryView
)

urlpatterns = [
    path("chat/notifications/", GetNotificationChatsToProviderView.as_view(), name='chat-notifications-list'),
    path("chat/<int:pk>/notifications/", UpdateNotificationChatInProviderView.as_view(), name='chat-notifications'),
    path("providers/chat/", GetProvidersChatView.as_view(), name='providers-chat'),
    path("conversation/", GetProviderChatInformationView.as_view(), name='providers-pk-chat'),
    path("patients/chat/", GetPatientsChatView.as_view(), name='patients-chat'),
    # path("patients/chat/<int:pk>/", UpdateChatStatusInPatientView.as_view(), name='update-chat-status'),
    path("patients/<str:pk>/chat/messages/", GetPatientChatInformationView.as_view(), name='patients-pk-chat-message'),
    # path("patients/<str:pk>/chat/history/", SingleToSingleChatHistoryView.as_view(), name='patients-pk-chat-history'),
]
