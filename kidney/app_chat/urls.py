from django.urls import path
from .views import (
    GetNotificationChatsToProviderView,
    UpdateNotificationChatInProviderView,
    GetProvidersChatView,
    GetProviderChatInformationView,
    GetPatientsChatView,
    UpdateChatStatusInView,
    GetPatientChatInformationView,
)

urlpatterns = [
    path("chat/notifications/", GetNotificationChatsToProviderView.as_view(), name='chat-notifications-list'),
    path("chat/<int:pk>/notifications/", UpdateNotificationChatInProviderView.as_view(), name='chat-notifications'),
    path("providers/chat/", GetProvidersChatView.as_view(), name='providers-chat'),
    path("providers/chat/<int:id>/", UpdateChatStatusInView.as_view(), name="mark-chat-as-read"),
    path("conversation/<str:pk>/", GetProviderChatInformationView.as_view(), name='providers-pk-chat'),
    path("patients/chat/", GetPatientsChatView.as_view(), name='patients-chat'),
    path("patients/chat/<int:id>/", UpdateChatStatusInView.as_view(), name="mark-chat-as-read"),
    path("patients/<str:pk>/chat/messages/", GetPatientChatInformationView.as_view(), name='patients-pk-chat-message'),
]
