from django.contrib import admin
from .models import DietPlan, SubDietPlan

@admin.register(DietPlan)
class AdminDietPlan(admin.ModelAdmin):
    pass

@admin.register(SubDietPlan)
class AdminSubDietPlan(admin.ModelAdmin):
    pass