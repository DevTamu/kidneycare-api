from django.urls import path
from .views import (
    CreateAppointmentView,
    GetAppointmentInProviderView,
    GetAppointmentInAdminView,
    GetAppointmentDetailsInProviderView
)

urlpatterns = [
    path('patient/appointment', CreateAppointmentView.as_view(), name='create-appointment'),
    path('get-provider-appointment/', GetAppointmentInProviderView.as_view(), name='get_all_patient_appointment'),
    path('patient/appointment-details/<str:id>/', GetAppointmentDetailsInProviderView.as_view(), name='get_patient_appointment'),
    path('get-admin-appointment/', GetAppointmentInAdminView.as_view(), name='get-admin-appointment'),
]
