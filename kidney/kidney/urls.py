from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_authentication.urls')),
    path('news-event/', include('app_news_event.urls')),
    path('api/', include('app_appointment.urls')),
    path('api/', include('app_chat.urls')),
    path('api/', include('app_treatment.urls')),
    path('api/', include('app_analytics.urls')),
    path('api/', include('app_schedule.urls')),
    path('api/', include('app_diet_plan.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
