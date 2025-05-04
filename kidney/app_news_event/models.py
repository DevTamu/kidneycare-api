from django.db import models
from kidney.models import TimestampModel
from django.utils import timezone
import datetime

class NewsEvent(TimestampModel):
    title = models.CharField(max_length=100)
    date = models.DateField(blank=True,null=True)
    time = models.TimeField(blank=True,null=True)
    description = models.CharField(max_length=255)
    category = models.CharField()

    def __str__(self):
        return f"{self.category} - {self.title}"
    
class NewsEventImage(TimestampModel):
    news_event = models.ForeignKey(NewsEvent, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='upload/news_event_image/', blank=True, null=True)

    def __str__(self):
        return f"{self.news_event.title}"