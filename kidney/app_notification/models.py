from django.db import models
from kidney.models import TimestampModel
from app_appointment.models import Appointment

class Notification(TimestampModel):

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='notifications')
    fcm_token = models.CharField(max_length=255, null=True)
    sent_at = models.DateTimeField(auto_created=True, auto_now=True, null=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.appointment.user.username}"
