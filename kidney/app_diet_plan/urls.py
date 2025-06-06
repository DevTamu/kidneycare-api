from django.urls import path
from .views import (
    CreateDietPlanView,
    GetPatientHealthStatusView,
    GetPatientDietPlanLimitOneView,
    GetPatientAllDietPlanView,
    GetPatientDietPlanWithIDView,
    GetDietPlanInAdminView,
    GetAllDietPlansInAdminView,
    GetPatientMedicationView,
    GetDietPlanStatusInProviderView,
    CreatePatientHealthStatusView
)

urlpatterns = [
        path("patients/<str:pk>/diet-plan/", CreateDietPlanView.as_view(), name='create-diet-plan'),
        path("patients/<str:pk>/health-diet-plan/", CreatePatientHealthStatusView.as_view(), name='create-diet-plan'),
        path("patients/health-status/", GetPatientHealthStatusView.as_view(), name='get-health-status'),
        path("patients/diet-plan/", GetPatientDietPlanLimitOneView.as_view(), name='get-diet-plan'),
        path("patients/diet-plan/<int:pk>/", GetPatientDietPlanWithIDView.as_view(), name='get-diet-plan-by-id'),
        path("patients/diet-plans/", GetPatientAllDietPlanView.as_view(), name='get-all-diet-plan'),
        path('diet-plan/<int:sub_diet_plan_id>/', GetDietPlanInAdminView.as_view(), name='patient-health-status'),
        path('patients/<str:pk>/all-diet-plans/', GetAllDietPlansInAdminView.as_view(), name='all-diet-plans'),
        path('patients/medications/', GetPatientMedicationView.as_view(), name='patient-medication'),
        path('patients/medications/<int:pk>/', GetPatientMedicationView.as_view(), name='patient-medication'),
        path('patients/<str:pk>/health-status/', GetDietPlanStatusInProviderView.as_view(), name='patient-medication'),

]
