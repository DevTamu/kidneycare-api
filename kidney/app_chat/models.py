from django.db import models
from kidney.models import TimestampModel
from app_authentication.models import User
# Create your models here.
from django.utils import timezone
class Message(TimestampModel):

    status_choices = [
        ('sent', 'sent'),
        ('delivered', 'delivered'),
        ('read', 'read')
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_messages')
    content = models.TextField(max_length=255, null=True)
    read = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=status_choices, default='sent')
    date_sent = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from: {self.sender.username} to {self.receiver.username}"
