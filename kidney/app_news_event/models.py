from django.db import models
from kidney.models import TimestampModel
from cloudinary_storage.storage import MediaCloudinaryStorage

class NewsEvent(TimestampModel):
    title = models.CharField(max_length=100)
    date = models.DateField(blank=True,null=True)
    time = models.TimeField(auto_created=True, auto_now=True, null=True)
    description = models.TextField(max_length=2000)
    category = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.category} - {self.title}"
    
class NewsEventImage(TimestampModel):
    news_event = models.ForeignKey(NewsEvent, on_delete=models.CASCADE, related_name='news_events')
    image = models.ImageField(storage=MediaCloudinaryStorage(), upload_to='news_event_image/', blank=True, null=True)

    def __str__(self):
        return f"{self.news_event.title}"