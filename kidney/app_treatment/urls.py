from django.urls import path
from .views import (
    CreateTreatmentFormView,
    GetPatientHealthMonitoringView,
    GetAssignedPatientHealthMonitoringView,
    GetPatientsTreatmentHistoryView,
    GetPatientTreatmentView,
    DeletePatientsTreatmentHistoryView
)

urlpatterns = [
    path('patients/<str:pk>/treatment-form/', CreateTreatmentFormView.as_view(), name='create-treatment-form'),
    path('patients/health-monitoring/', GetPatientHealthMonitoringView.as_view(), name='patient-health-monitoring'),
    path('patients/<str:pk>/treatment-history/', GetPatientsTreatmentHistoryView.as_view(), name='patient-treatment-history'),
    path('patients/<str:pk>/treatment/<int:id>/', GetPatientTreatmentView.as_view(), name='patient-treatment'),
    path('patients/<str:pk>/treatment-history/<int:id>/', DeletePatientsTreatmentHistoryView.as_view(), name='delete-patient-treatment-history'),
    path('health-monitoring/', GetAssignedPatientHealthMonitoringView.as_view(), name='caregiver-health-monitoring')
]
