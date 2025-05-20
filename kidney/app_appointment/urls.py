from django.urls import path
from .views import (
    CreateAppointmentView,
    GetAppointmentInProviderView,
    GetPatientInformationView,
    UpdateAppointmentInPatientView,
    AddAppointmentDetailsInAdminView,
    GetPatientAppointmentHistoryView,
    GetPendingAppointsmentsInAdminView,
    CancelAppointmentView,
    GetPatientUpcomingAppointmentView,
    GetPatientUpcomingAppointmentsInHomeView,
    GetAllPatientUpcomingAppointmentInAppointmentView,
    CancelPatientUpcomingAppointmentInAppointmentView
)

urlpatterns = [
    path('patient/create-appointment/', CreateAppointmentView.as_view(), name='create-appointment'),
    path('patient/update-appointment/<int:pk>/', UpdateAppointmentInPatientView.as_view(), name='update-appointment'),
    path('add/appointment-details/<int:pk>/', AddAppointmentDetailsInAdminView.as_view(), name='add-appointment-details'),
    path('patient/appointments/', GetAppointmentInProviderView.as_view(), name='all-patient-appointments'),
    path('patient-information/<str:pk>/', GetPatientInformationView.as_view(), name='patient-information'),
    path('patient/appointment-history/<str:pk>/', GetPatientAppointmentHistoryView.as_view(), name='patient-appointment-history'),
    path('patient/pending-appointments/', GetPendingAppointsmentsInAdminView.as_view(), name='patient-pending-appointments'),
    path('patient/cancel-appointment/<int:pk>/', CancelAppointmentView.as_view(), name='patient-cancel-appointment'),
    path('patient/upcoming-appointment/', GetPatientUpcomingAppointmentView.as_view(), name='patient-upcoming-appointment'),
    path('patient/upcoming-appointments/', GetPatientUpcomingAppointmentsInHomeView.as_view(), name='patient-upcoming-appointments'),
    path('patient/all-upcoming-appointments/', GetAllPatientUpcomingAppointmentInAppointmentView.as_view(), name='patient-upcoming-appointments'),
    path('patient/cancel-upcoming-appointment/<int:pk>/', CancelPatientUpcomingAppointmentInAppointmentView.as_view(), name='patient-cancel-appointment'),
]
