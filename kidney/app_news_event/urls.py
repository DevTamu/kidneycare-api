from django.urls import path
from .views import (
    AddNewsEventView,
    GetNewsEventView
)

urlpatterns = [
    path('add/', AddNewsEventView.as_view(), name='add'),
    path('get/', GetNewsEventView.as_view(), name='get')
]
    