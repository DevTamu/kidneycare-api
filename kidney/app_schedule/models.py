from django.db import models
from kidney.models import TimestampModel
# Create your models here.
from django.utils import timezone

class Schedule(TimestampModel):
    available_days = models.JSONField(default=list)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    date_created = models.DateField(null=True, blank=True)
