from django.contrib import admin
from app_authentication.models import User, UserInformation, Profile
# Register your models here.


@admin.register(UserInformation)
class UserInformationAdmin(admin.ModelAdmin):
    pass

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
