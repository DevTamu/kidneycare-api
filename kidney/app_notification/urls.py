from django.urls import path
from .views import (
    NotificationsInPatientView
)

urlpatterns = [
    path('notifications/', NotificationsInPatientView.as_view(), name='notifications')
]
