from django.contrib import admin
from app_authentication.models import User, UserInformation, Profile, OTP
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)

@admin.register(UserInformation)
class UserInformationAdmin(admin.ModelAdmin):
    pass

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
