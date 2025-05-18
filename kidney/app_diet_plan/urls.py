from django.urls import path
from .views import (
    AddDietPlanView,
    GetPatientHealthStatusView,
    GetPatientDietPlanView,
    GetPatientAllDietPlanView
)

urlpatterns = [
    path("add/patient/diet-plan/", AddDietPlanView.as_view(), name='add-diet-plan'),
    path("get/patient/health-status/", GetPatientHealthStatusView.as_view(), name='get-health-status'),
    path("get/patient/diet-plan/", GetPatientDietPlanView.as_view(), name='get-diet-plan'),
    path("get/patient/all-diet-plan/", GetPatientAllDietPlanView.as_view(), name='get-all-diet-plan'),
]
