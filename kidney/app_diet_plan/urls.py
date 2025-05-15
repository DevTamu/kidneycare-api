from django.urls import path
from .views import (
    AddDietPlanView
)

urlpatterns = [
    path("add/patient/diet-plan/", AddDietPlanView.as_view(), name='add-diet-plan')
]
