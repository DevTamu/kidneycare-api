from .serializers import (
    RegisterSerializer,
    LoginObtainPairSerializer,
    RefreshTokenSerializer,
    ChangePasswordSerializer,
    LogoutSerializer,
    VerifyOTPSerializer,
    SendOTPSerializer,
    ResendOTPSerializer
)
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics
from kidney.utils import ResponseMessageUtils, get_tokens_for_user
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
import json
from django.contrib.auth import logout
import logging
from .models import OTP
from rest_framework import serializers

logger = logging.getLogger(__name__)

class SendOTPView(generics.CreateAPIView):
    serializer_class = SendOTPSerializer

    def post(self, request):

        try:
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                result = serializer.save()
                return ResponseMessageUtils(message="OTP Sent to your email", data=result, status_code=status.HTTP_200_OK)
            return ResponseMessageUtils(message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Error", str(e))
            return ResponseMessageUtils(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class VerifyOTPView(generics.UpdateAPIView):
    queryset = OTP.objects.all()
    serializer_class = VerifyOTPSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ResponseMessageUtils(message="OTP verified successfully.", status_code=status.HTTP_200_OK)


class ResendOTPView(generics.UpdateAPIView):
    queryset = OTP.objects.all()
    serializer_class = ResendOTPSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            #access validated data
            result = serializer.save()
            return ResponseMessageUtils(message="Successfully Resend the OTP", data={"otp_token": result.otp_token}, status_code=status.HTTP_200_OK)
        return ResponseMessageUtils(message=serializer.errors["message"][0], status_code=status.HTTP_400_BAD_REQUEST)
    

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):

        try:
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                #save the data
                user_profile = serializer.save()
                user = user_profile.user

                token = get_tokens_for_user(user)

                return ResponseMessageUtils(
                    message="Account Registered Successfully",
                    data={
                        "access": token["access"],
                        "refresh": token["refresh"],
                        "email": user.username,
                        "picture": request.build_absolute_uri(user_profile.picture.url) if user_profile.picture else None 
                    },
                    status_code=status.HTTP_201_CREATED
                )
            logger.error(serializer.errors)
            return ResponseMessageUtils(
                message=serializer.errors["message"][0],
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except serializers.ValidationError as e:
            logger.error(f"Validation error: {e.detail}")
            # Extract the first error message
            error_field = list(e.detail.keys())[0]
            error_message = e.detail[error_field][0]
            
            return ResponseMessageUtils(
                message=f"Validation error: {error_message}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except KeyError as e:
            logger.error(f"Missing field error: {str(e)}")
            return ResponseMessageUtils(
                message=f"Missing required field: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(e)
            return ResponseMessageUtils(
                message=f"Something went wrong: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            

class LoginView(TokenObtainPairView):
    serializer_class = LoginObtainPairSerializer


class RefreshTokenView(TokenRefreshView):
    serializer_class = RefreshTokenSerializer

class ChangePasswordView(generics.UpdateAPIView):
    
    permission_classes = [IsAuthenticated] #must be authenticated to change password

    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        
        try:
            serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(message="Password updated Successfully", status_code=status.HTTP_200_OK)
            return ResponseMessageUtils(message=serializer.errors["message"][0], status_code=status.HTTP_400_BAD_REQUEST)
        except AuthenticationFailed as e:
            logger.error(f"Authentication failed: {str(e)}")
            return ResponseMessageUtils(message="Token has expired or is invalid. Please log in again.", status_code=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Error occurred during password change: {str(e)}")
            return ResponseMessageUtils(message="An error occured during change password", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication] #only JWT Auth
    permission_classes = [IsAuthenticated]  #must be authenticated to logout
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        try:
            if serializer.is_valid():
                serializer.save()
                logout(request)
                return ResponseMessageUtils(message="Successfully logged out", status_code=status.HTTP_200_OK) 
            return ResponseMessageUtils(message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            return ResponseMessageUtils(message="Error Occured during logout", status_code=status.HTTP_400_BAD_REQUEST) 
