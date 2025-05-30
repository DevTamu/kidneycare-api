from django.urls import path
from .views import (
    CreateTreatmentFormView
)

urlpatterns = [
    path('patients/<str:pk>/treatment-form/', CreateTreatmentFormView.as_view(), name='creat-treatment-form')
]
