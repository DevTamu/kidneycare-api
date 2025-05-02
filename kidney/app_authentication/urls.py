from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    RefreshTokenView,
    LogoutView,
    ChangePasswordView,
    SendOTPView,
    VerifyOTPView
)

urlpatterns = [
    path('register/send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('register/verify-otp/', VerifyOTPView.as_view(), name='send-otp'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password')
]
