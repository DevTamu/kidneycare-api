from django.db import models
from kidney.models import TimestampModel
from app_authentication.models import User

class Appointment(TimestampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Appointment"

class AssignedMachine(models.Model):
    assigned_machine = models.JSONField(blank=True, null=True)  #list of assigned machines
    status = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Assigned Machine: {self.assigned_machine}"

class AssignedAppointment(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    assigned_machine = models.ForeignKey(AssignedMachine, on_delete=models.CASCADE, related_name='assigned_appointments')
    assigned_provider = models.JSONField(blank=True, null=True)  #list of assigned providers


    def __str__(self):
        return f"{self.appointment.user.username} Assigned"

