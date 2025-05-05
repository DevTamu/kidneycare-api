from django.urls import path
from .views import (
    CreateAppointmentView
)

urlpatterns = [
    path('create/', CreateAppointmentView.as_view(), name='create')
]
