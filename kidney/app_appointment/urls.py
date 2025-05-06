from django.urls import path
from .views import (
    CreateAppointmentView,
    GetAppointmentInProviderView,
    GetAppointmentInAdminView
)

urlpatterns = [
    path('patient/appointment', CreateAppointmentView.as_view(), name='create-appointment'),
    path('get-provider-appointment/', GetAppointmentInProviderView.as_view(), name='get-provider-appointment'),
    path('get-admin-appointment/', GetAppointmentInAdminView.as_view(), name='get-admin-appointment'),
]
