from django.urls import path
from .views import (
    CreateTreatmentFormView,
    GetPatientHealthMonitoringView
)

urlpatterns = [
    path('patients/<str:pk>/treatment-form/', CreateTreatmentFormView.as_view(), name='create-treatment-form'),
    path('patients/health-monitoring/', GetPatientHealthMonitoringView.as_view(), name='patient-health-monitoring')
]
