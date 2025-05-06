from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from kidney.models import TimestampModel
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Patient', 'Patient'),
        ('Admin', 'Admin'),
        ('Nurse', 'Nurse'),
        ('Head Nurse', 'Head Nurse'),
        ('Provider', 'Provider'),
        ('Caregiver', 'Caregiver'),
    )

    middlename = models.CharField(max_length=50, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Profile(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    picture = models.ImageField(upload_to=("upload/profile_picture/"), blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class UserInformation(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    suffix_name = models.BooleanField(default=False)
    birthdate = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    contact = models.CharField(max_length=11, blank=True, null=True)
    address = models.CharField(max_length=100, null=True)
    age = models.CharField(max_length=10, null=True)


    def __str__(self):
        return f"Information of {self.user.username}"
    

class OTP(TimestampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    otp_token = models.UUIDField(default=uuid.uuid4(), unique=True)

    def is_otp_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=3)
