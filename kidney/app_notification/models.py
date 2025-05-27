from django.db import models
from kidney.models import TimestampModel
from app_appointment.models import Appointment

class Notification(TimestampModel):

    STATUS_CHOICES = [
        ('pending', 'Pending'),       # Created but not yet sent
        ('approved', 'Approved'),       # Created but not yet sent
        ('scheduled', 'Scheduled'),   # Scheduled to be sent later
        ('maintenance', 'Maintenance'),   # Scheduled to be sent later
        ('declined', 'Declined'),   # Cancelled before sending
    ]

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='notifications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(auto_created=True, auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.appointment.user.username}"
