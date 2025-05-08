from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_authentication.urls')),
    path('news-event/', include('app_news_event.urls')),
    path('api/', include('app_appointment.urls')),
    path('api/', include('app_chat.urls'))
]
