from django.db import models
from kidney.models import TimestampModel
# Create your models here.


class Schedule(TimestampModel):
    schedule_days = models.JSONField(default=list)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
