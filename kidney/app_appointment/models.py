from django.db import models
from kidney.models import TimestampModel
from app_authentication.models import User
import uuid
from django.utils import timezone

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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(blank=True, null=True, default=None)
    time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=appointment_status, default='Pending')

    def __str__(self):
        return f"{self.user.username} Appointment - {self.id}"

class AssignedMachine(models.Model):
    assigned_machine_appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='assigned_machine_appointment', null=True, blank=True)
    assigned_machine = models.CharField(blank=True, null=True)  #list of assigned machines
    status = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.assigned_machine_appointment.user.username} - Assigned Machine: {self.assigned_machine}"
    
class AssignedProvider(models.Model):
    assigned_provider = models.ForeignKey(User, on_delete=models.CASCADE, default=uuid.uuid4, related_name='assigned_user') 
    assigned_patient_appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='assigned_patient_appointment', null=True, blank=True)

    def __str__(self):
        return f"Assigned Provider: {self.assigned_provider.username}"


class AssignedAppointment(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='assigned_appointments')
    assigned_machine = models.ForeignKey(AssignedMachine, on_delete=models.CASCADE, related_name='assigned_machine_appointments', null=True, blank=True)
    assigned_provider = models.ForeignKey(AssignedProvider, on_delete=models.CASCADE, related_name='assigned_provider_appointment', null=True, blank=True)
  
    def __str__(self):
        return f'Assigned Appointment: {self.appointment.user.username}'




