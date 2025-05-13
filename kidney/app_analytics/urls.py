from django.urls import path
from .views import (
    GetPatientAnalyticsView
)

urlpatterns = [
    path('patient/analytics/', GetPatientAnalyticsView.as_view(), name='patient-analytics')
]
