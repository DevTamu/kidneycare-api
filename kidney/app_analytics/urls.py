from django.urls import path
from .views import (
    GetPatientAnalyticsView,
    GetAppointmentAnalyticsView,
    GetProviderAnalyticsView,
    GetAppointmentStatusBreakdownView,
    GetPatientTrackingGenderView
)

urlpatterns = [
    path('patients/analytics/', GetPatientAnalyticsView.as_view(), name='patient-analytics'),
    path('appointments/analytics/', GetAppointmentAnalyticsView.as_view(), name='appointment-analytics'),
    path('providers/analytics/', GetProviderAnalyticsView.as_view(), name='provider-analytics'),
    path('appointments-breakdown/analytics/', GetAppointmentStatusBreakdownView.as_view(), name='appointment-status-breakdown-analytics'),
    path('patients/trackings/', GetPatientTrackingGenderView.as_view(), name='patient-trackings'),
]
