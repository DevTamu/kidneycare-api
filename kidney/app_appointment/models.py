from django.db import models
from kidney.models import TimestampModel
from app_authentication.models import User
import uuid

class Appointment(TimestampModel):
    appointment_status = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Check-In', 'Check-In'),
        ('In-Progress', 'In-Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('No Show', 'No Show'),
        ('Rescheduled', 'Rescheduled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=appointment_status, default='Pending')

    def __str__(self):
        return f"{self.user.username} Appointment"

class AssignedMachine(models.Model):
    assigned_machine = models.JSONField(blank=True, null=True)  #list of assigned machines
    status = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Assigned Machine: {self.assigned_machine}"
    
class AssignedProvider(models.Model):
    assigned_provider = models.ForeignKey(User, on_delete=models.CASCADE, default=uuid.uuid4, related_name='assigned_user')  #list of assigned providers
    assigned_provider_appointments = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='provider_assignments', null=True, blank=True)
    def __str__(self):
        return f"Assigned Provider: {self.assigned_provider.username}"


class AssignedAppointment(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='assigned_appointments')
    assigned_machines = models.ManyToManyField(AssignedMachine, related_name='assigned_machine_appointments')
    assigned_providers = models.ManyToManyField(AssignedProvider, related_name='assigned_appointments')

    def __str__(self):
        username_data = []
        for username in self.assigned_providers.all().values_list('assigned_provider__username'):
            username_data.append(username)
        
        return f'{username_data} Assigned'
    



