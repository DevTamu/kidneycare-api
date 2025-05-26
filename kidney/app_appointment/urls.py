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
    CancelPatientUpcomingAppointmentInAppointmentView,
    GetPatientAppointmentDetailsInAdminView,
    GetUpcomingAppointmentDetailsInPatientView
)

urlpatterns = [
    path('patient/create-appointment/', CreateAppointmentView.as_view(), name='create-appointment'),
    path('patient/update-appointment/<int:pk>/', UpdateAppointmentInPatientView.as_view(), name='update-appointment'),
    path('appointment-details/<int:pk>/', AddAppointmentDetailsInAdminView.as_view(), name='add-appointment-details'),
    path('patient/appointment-details/<int:pk>/', GetPatientAppointmentDetailsInAdminView.as_view(), name='get-appointment-details'),
    path('patient/appointments/', GetAppointmentInProviderView.as_view(), name='all-patient-appointments'),
    path('patient-information/<str:pk>/', GetPatientInformationView.as_view(), name='patient-information'),
    path('patient/appointment-history/<str:pk>/', GetPatientAppointmentHistoryView.as_view(), name='patient-appointment-history'),
    path('patient/pending-appointments/', GetPendingAppointsmentsInAdminView.as_view(), name='patient-pending-appointments'),
    path('patient/cancel-appointment/<int:pk>/', CancelAppointmentView.as_view(), name='patient-cancel-appointment'),
    path('patient/upcoming-appointment/', GetPatientUpcomingAppointmentView.as_view(), name='patient-upcoming-appointment'),
    path('patient/upcoming-appointment-details/<int:pk>/', GetUpcomingAppointmentDetailsInPatientView.as_view(), name='patient-upcoming-appointment-details'),
    path('patient/upcoming-appointments/', GetPatientUpcomingAppointmentsInHomeView.as_view(), name='patient-upcoming-appointments'),
    path('patient/cancel-upcoming-appointment/<int:pk>/', CancelPatientUpcomingAppointmentInAppointmentView.as_view(), name='patient-cancel-appointment'),
]
