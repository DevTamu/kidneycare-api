from django.urls import path
from .views import (
    AddNewsEventView,
    GetNewsEventView
)

urlpatterns = [
    path('add/news-event/', AddNewsEventView.as_view(), name='add'),
    path('get/news-event/', GetNewsEventView.as_view(), name='get')
]
    