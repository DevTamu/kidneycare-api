from django.urls import path
from .views import (
    CreateDietPlanView,
    GetPatientHealthStatusView,
    GetPatientDietPlanLimitOneView,
    GetPatientAllDietPlanView,
    GetPatientDietPlanWithIDView
)

urlpatterns = [
        path("patients/<str:pk>/diet-plan/", CreateDietPlanView.as_view(), name='create-diet-plan'),
        path("patients/health-status/", GetPatientHealthStatusView.as_view(), name='get-health-status'),
        path("patients/diet-plan/", GetPatientDietPlanLimitOneView.as_view(), name='get-diet-plan'),
        path("patients/diet-plan/<int:pk>/", GetPatientDietPlanWithIDView.as_view(), name='get-diet-plan-by-id'),
        path("patients/diet-plans/", GetPatientAllDietPlanView.as_view(), name='get-all-diet-plan'),
]
