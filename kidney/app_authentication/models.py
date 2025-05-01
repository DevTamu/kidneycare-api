from django.db import models, transaction
from django.contrib.auth.models import User
from kidney.models import TimestampModel
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ROLE_CHOICES = (
        ('PATIENT', 'Patient'),
        ('ADMIN', 'Admin'),
        ('NURSE', 'Nurse')
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Profile(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    picture = models.ImageField(upload_to=("profile_picture/"), blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"



class UserInformation(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    suffix_name = models.CharField(max_length=10, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"Information of {self.user.username}"
