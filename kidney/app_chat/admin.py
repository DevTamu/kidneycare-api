from django.contrib import admin
from .models import Message
# Register your models here.
@admin.register(Message)
class AdminMessage(admin.ModelAdmin):
    pass