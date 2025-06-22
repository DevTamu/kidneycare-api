from django.urls import path
from .views import (
    AddNewsEventView,
    GetNewsEventView,
    GetNewsEventsView,
    GetNewsEventLimitByTwoView,
    GetNewsEventWithIDView
)

urlpatterns = [
    path('add/news-event/', AddNewsEventView.as_view(), name='add'),
    path('news-event/', GetNewsEventView.as_view(), name='get-news-event'),
    path('news-events/', GetNewsEventsView.as_view(), name='get-news-events'),
    path('news-event/<int:pk>/', GetNewsEventWithIDView.as_view(), name='get-news-event-by-id'),
    # path('get/limit-news-event/', GetNewsEventLimitByTwoView.as_view(), name='get-news-event-limit'),
]
    