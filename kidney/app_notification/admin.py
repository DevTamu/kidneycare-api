from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class AdminNotification(admin.ModelAdmin):
    readonly_fields = ('created_at',)