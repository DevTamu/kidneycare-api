from django.urls import path
from .views import (
    AddNewsEventView,
    GetNewsEventView,
    UpdateNewsEventView,
    DeleteNewsEventView
)

urlpatterns = [
    path('add/news-event/', AddNewsEventView.as_view(), name='add-news-event'),
    path('get/news-event/', GetNewsEventView.as_view(), name='get-news-event'),
    path('update/news-event/<str:pk>/', UpdateNewsEventView.as_view(), name='update-news-event'),
    path('delete/news-event/<str:pk>/', DeleteNewsEventView.as_view(), name='delete-news-event')
]
    