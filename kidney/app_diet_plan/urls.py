from django.urls import path
from .views import (
    AddDietPlanView,
    GetPatientHealthStatusView,
    GetPatientDietPlanView,
    GetPatientAllDietPlanView,
    GetPatientDietPlanWithIDView
)

urlpatterns = [
    path("add/patient/diet-plan/", AddDietPlanView.as_view(), name='add-diet-plan'),
    path("patient/health-status/", GetPatientHealthStatusView.as_view(), name='get-health-status'),
    path("patient/diet-plan/", GetPatientDietPlanView.as_view(), name='get-diet-plan'),
    path("patient/all-diet-plan/", GetPatientAllDietPlanView.as_view(), name='get-all-diet-plan'),
    path("patient/diet-plan/<int:pk>/", GetPatientDietPlanWithIDView.as_view(), name='get-diet-plan-by-id'),
]
