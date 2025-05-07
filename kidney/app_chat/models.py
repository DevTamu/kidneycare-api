from django.db import models
from kidney.models import TimestampModel
from app_authentication.models import User
# Create your models here.

class Message(TimestampModel):
    #sender message user relationship
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_messages')
    #receiver message user relationship
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_messages')
    content = models.TextField(max_length=255, null=True)
    read = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[('sent', 'Sent'), ('delivered', 'Delivered'), ('read', 'Read')], default='sent')

    def __str__(self):
        return f"Message from: {self.sender.username} to {self.receiver.username}"
