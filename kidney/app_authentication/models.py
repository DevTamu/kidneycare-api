from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from kidney.models import TimestampModel
from django.contrib.auth.models import AbstractUser
import uuid
from cloudinary_storage.storage import MediaCloudinaryStorage

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('admin', 'Admin'),
        ('nurse', 'Nurse'),
        ('head nurse', 'Head Nurse'),
        ('caregiver', 'Caregiver'),
    )
    middlename = models.CharField(max_length=50, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, default='offline')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Profile(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='user_profile')
    picture = models.ImageField(storage=MediaCloudinaryStorage(), max_length=500, upload_to=("profile_picture/"), blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class UserInformation(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='user_information')
    birthdate = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    contact = models.CharField(max_length=11, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    age = models.CharField(max_length=10, null=True)


    def __str__(self):
        return f"Information of {self.user.username}"
    
class OTP(TimestampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='user_otp')
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    otp_token = models.UUIDField(default=uuid.uuid4, unique=True)

    def is_otp_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=3)
    
class Caregiver(TimestampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caregiver')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='added_caregivers')
    def __str__(self):
        return f"{self.user.username} - {self.user.role}"