from django.urls import path
from .views import (
    GetPatientAnalyticsView,
    GetAppointmentAnalyticsView,
    GetProviderAnalyticsView,
    GetAppointmentStatusBreakdownView
)

urlpatterns = [
    path('analytics/patients/', GetPatientAnalyticsView.as_view(), name='patient-analytics'),
    path('analytics/appointment/', GetAppointmentAnalyticsView.as_view(), name='appointment-analytics'),
    path('analytics/provider/', GetProviderAnalyticsView.as_view(), name='provider-analytics'),
    path('analytics/appointment-status-breakdown/', GetAppointmentStatusBreakdownView.as_view(), name='appointment-status-breakdown-analytics'),
]
