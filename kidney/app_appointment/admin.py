from django.contrib import admin
from .models import AssignedAppointment, Appointment, AssignedMachine
# Register your models here.

@admin.register(Appointment)
class AdminAppointment(admin.ModelAdmin):
    pass

@admin.register(AssignedAppointment)
class AdminAppointment(admin.ModelAdmin):
    pass

@admin.register(AssignedMachine)
class AdminAssignedMachine(admin.ModelAdmin):
    pass

