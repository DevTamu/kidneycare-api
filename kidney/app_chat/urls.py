from django.urls import path
from .views import (
    GetNotificationChatsToProviderView,
    GetPatientsChatView,
    # UpdateNotificationChatInProviderView,
    GetProvidersChatView,
    GetProviderChatInformationView,
    GetPatientsChatView,
    UpdateChatStatusInView,
    GetPatientChatInformationView,
    GetPatientChatInformationInProviderView
)

urlpatterns = [
    path("patients/chat/notifications/", GetNotificationChatsToProviderView.as_view(), name='chat-notifications-list'),
    path("patients/<str:pk>/conversation/", GetPatientChatInformationInProviderView.as_view(), name='providers-pk-chat'),
    path("patients/<str:pk>/chat/notifications/", UpdateChatStatusInView.as_view(), name='mark-provider-chat-as-read-1'),
    path("providers/chat/", GetProvidersChatView.as_view(), name='providers-chat'),
    path("providers/<str:pk>/chat/", UpdateChatStatusInView.as_view(), name="mark-provider-chat-as-read"),
    path("conversation/<str:pk>/", GetProviderChatInformationView.as_view(), name='providers-pk-chat'),
    path("patients/chat/", GetPatientsChatView.as_view(), name='patients-chat'),
    path("patients/<str:pk>/chat/", UpdateChatStatusInView.as_view(), name="mark-patient-chat-as-read"),
    path("patients/<str:pk>/chat/messages/", GetPatientChatInformationView.as_view(), name='patients-pk-chat-message'),
]
