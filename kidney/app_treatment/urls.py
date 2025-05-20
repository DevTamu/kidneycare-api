from django.urls import path
from .views import (
    CreateTreatmentFormView
)

urlpatterns = [
    path('create/treatment-form/', CreateTreatmentFormView.as_view(), name='creat-treatment-form')
]
