from django.contrib import admin
from .models import (
    NewsEvent,
    NewsEventImage
)
# Register your models here.

@admin.register(NewsEvent)
class AdminNewsEvent(admin.ModelAdmin):
    pass

@admin.register(NewsEventImage)
class AdminNewsEventImage(admin.ModelAdmin):
    pass