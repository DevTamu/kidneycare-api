from django.urls import path
from .views import (
    AddNewsEventView,
    GetNewsEventView,
    GetNewsEventLimitByTwoView,
    GetNewsEventWithIDView
)

urlpatterns = [
    path('add/news-event/', AddNewsEventView.as_view(), name='add'),
    path('get/news-event/', GetNewsEventView.as_view(), name='get-news-event'),
    path('get/<int:pk>/news-event/', GetNewsEventWithIDView.as_view(), name='get-news-event-by-id'),
    path('get/limit-news-event/', GetNewsEventLimitByTwoView.as_view(), name='get-news-event-limit'),
]
    