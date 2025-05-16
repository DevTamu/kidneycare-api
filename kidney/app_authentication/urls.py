from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    RefreshTokenView,
    LogoutView,
    ChangePasswordView,
    SendOTPView,
    VerifyOTPView,
    ResendOTPView,
    AddAccountHealthCareProviderView,
    ChangePasswordHealthCareProviderView,
    GetUsersView,
    GetUserView,
    GetUserRoleView,
    GetHealthCareProvidersView
)

urlpatterns = [
    path('register/send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('register/verify-otp/', VerifyOTPView.as_view(), name='send-otp'),
    path('register/resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('provider/add-account/', AddAccountHealthCareProviderView.as_view(), name='provider-add-account'),
    path('provider/change-password/', ChangePasswordHealthCareProviderView.as_view(), name='provider-change-password'),
    path('get/patients/', GetUsersView.as_view(), name='get-users'),
    path('get/patient/<str:id>/', GetUserView.as_view(), name='get-user'),
    path('user/role/', GetUserRoleView.as_view(), name='get-user-role'),
    path('get/providers/', GetHealthCareProvidersView.as_view(), name='get-providers'),
]
