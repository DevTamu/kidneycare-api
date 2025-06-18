from django.urls import path
from .views import (
    CreateScheduleView,
    GetScheduleView
)

urlpatterns = [
    path('create/schedule/', CreateScheduleView.as_view(), name='create-schedule'),
    path('schedules/', GetScheduleView.as_view(), name='get-schedule'),
]
