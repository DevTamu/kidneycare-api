from django.db import models
from kidney.models import TimestampModel
from app_appointment.models import User

class Treatment(TimestampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='treatment', null=True)
    diagnosis = models.CharField(max_length=100, null=True, blank=True)
    nephrologist = models.CharField(max_length=100, null=True, blank=True)
    last_treatment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Treatment'


class Prescription(models.Model):
    treatment = models.OneToOneField(Treatment, on_delete=models.CASCADE, related_name='treatment_prescription')
    weight = models.CharField(null=True, blank=True)
    weight_pre = models.FloatField(null=True, blank=True)
    weight_post = models.FloatField(null=True, blank=True)
    blood_pressure_pre = models.CharField(null=True, blank=True)
    blood_pressure_post = models.CharField(null=True, blank=True)
    pulse_pre = models.IntegerField(null=True, blank=True)
    pulse_post = models.IntegerField(null=True, blank=True)
    temp_pre = models.FloatField(null=True, blank=True)
    temp_post = models.FloatField(null=True, blank=True)
    respiratory_rate_pre = models.IntegerField(null=True, blank=True)
    respiratory_rate_post = models.IntegerField(null=True, blank=True)
    saturation_percentage_pre = models.IntegerField(null=True, blank=True)
    saturation_percentage_post = models.IntegerField(null=True, blank=True)
    rbs_pre = models.IntegerField(null=True, blank=True)
    rbs_post = models.IntegerField(null=True, blank=True)
    uf_time = models.CharField(null=True, blank=True)
    uf_goal = models.FloatField(null=True, blank=True)
    hepatitis_screening = models.CharField(null=True, blank=True, choices=[('Reactive', 'Reactive'),('Non-Reactive', 'Non-Reactive')])

    def __str__(self):
        return f'{self.treatment.user.username} Prescription'

class AccessType(models.Model):
    treatment = models.OneToOneField(Treatment, on_delete=models.CASCADE, related_name='treatment_access_type')
    access_type = models.JSONField(default=list)
    heparin = models.CharField(null=True, blank=True)
    flushing = models.CharField(null=True, blank=True)
    type = models.CharField(null=True, blank=True)

    def __str__(self):
        return f'{self.treatment.user.username} Access Type'

class TreatmentDetail(models.Model):
    treatment = models.OneToOneField(Treatment, on_delete=models.CASCADE, related_name='treatment_details')
    dialysis_number = models.IntegerField(null=True, blank=True)
    machine_number = models.IntegerField(null=True, blank=True)
    treatment_hours = models.CharField(null=True, blank=True)
    time_started = models.TimeField(null=True, blank=True)
    time_ended = models.TimeField(null=True, blank=True)
    left_via = models.CharField(null=True, blank=True, choices=[('Ambulatory', 'Ambulatory'),('Stretcher', 'Stretcher'),('Wheelchair', 'Wheelchair')])

    def __str__(self):
        return f'{self.treatment.user.username} Treatment Details'
    

class PreDialysis(models.Model):
    treatment = models.OneToOneField(Treatment, on_delete=models.CASCADE, related_name='treatment_pre_dialysis')
    general = models.CharField(null=True, blank=True)
    respiratory = models.CharField(null=True, blank=True)
    cardiac = models.CharField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.treatment.user.username} Pre Dialysis'

class PostDialysis(models.Model):
    treatment = models.OneToOneField(Treatment, on_delete=models.CASCADE, related_name='treatment_post_dialysis')
    general = models.CharField(null=True, blank=True)
    respiratory = models.CharField(null=True, blank=True)
    cardiac = models.CharField(null=True, blank=True)   

    def __str__(self):
        return f'{self.treatment.user.username} Post Dialysis'