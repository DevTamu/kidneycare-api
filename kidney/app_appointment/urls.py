from django.urls import path
from .views import (
    CreateAppointmentView,
    GetAppointmentInProviderView,
    # GetAppointmentInAdminView,
    GetAppointmentDetailsInProviderView,
    UpdateAppointmentInPatientView,
    AddAppointmentDetailsInAdminView
)

urlpatterns = [
    path('patient/appointment/', CreateAppointmentView.as_view(), name='create-appointment'),
    path('patient/update-appointment/<int:pk>/', UpdateAppointmentInPatientView.as_view(), name='update-appointment'),
    path('add/appointment-details/<int:pk>/', AddAppointmentDetailsInAdminView.as_view(), name='add-appointment-details'),
    path('patient/appointments/', GetAppointmentInProviderView.as_view(), name='get_all_patient_appointment'),
    path('patient/appointment-details/<str:pk>/', GetAppointmentDetailsInProviderView.as_view(), name='get_patient_appointment'),
    # path('get-admin-appointment/', GetAppointmentInAdminView.as_view(), name='get-admin-appointment'),
]
