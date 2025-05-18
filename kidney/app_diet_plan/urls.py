from django.urls import path
from .views import (
    AddDietPlanView,
    GetPatientDietPlanView
)

urlpatterns = [
    path("add/patient/diet-plan/", AddDietPlanView.as_view(), name='add-diet-plan'),
    path("get/patient/diet-plan/", GetPatientDietPlanView.as_view(), name='get-diet-plan')
]
