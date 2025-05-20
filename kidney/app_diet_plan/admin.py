from django.contrib import admin
from .models import DietPlan

@admin.register(DietPlan)
class AdminDietPlan(admin.ModelAdmin):
    pass