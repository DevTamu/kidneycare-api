from django.contrib import admin
from .models import AssignedAppointment, Appointment, AssignedMachine, AssignedProvider
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

@admin.register(AssignedProvider)
class AdminAssignedProvider(admin.ModelAdmin):
    pass
