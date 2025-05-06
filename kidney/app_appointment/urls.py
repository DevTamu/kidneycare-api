from django.urls import path
from .views import (
    CreateAppointmentView,
    GetAppointmentInProviderView
)

urlpatterns = [
    path('patient/', CreateAppointmentView.as_view(), name='create-appointment'),
    path('get/', GetAppointmentInProviderView.as_view(), name='get'),
]
