from django.urls import path
from .views import (
    GetUsersMessageView
)

urlpatterns = [
    path("chat/messages/<str:id>/", GetUsersMessageView.as_view(), name='chat-messages')
]
