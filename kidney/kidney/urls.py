from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app_authentication.views import ping

urlpatterns = [ 
    path('admin/', admin.site.urls),
    path('ping/', ping),
    path('', include('app_authentication.urls')),
    path('', include('app_news_event.urls')),
    path('', include('app_chat.urls')),
    path('', include('app_appointment.urls')),
    path('', include('app_treatment.urls')),
    path('', include('app_analytics.urls')),
    path('', include('app_schedule.urls')),
    path('', include('app_diet_plan.urls')),
    path('', include('app_notification.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
