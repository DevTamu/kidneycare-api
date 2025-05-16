from .serializers import (
    RegisterSerializer,
    LoginObtainPairSerializer,
    RefreshTokenSerializer,
    ChangePasswordSerializer,
    LogoutSerializer,
    VerifyOTPSerializer,
    SendOTPSerializer,
    ResendOTPSerializer,
    AddAccountHealthCareProviderSerializer,
    ChangePasswordHealthCareProviderSeriallizer,
    GetUsersSeriaizer,
    GetUserSeriaizer,
    GetUserRoleSerializer,
    GetHealthCareProvidersSerializer
)
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics
from kidney.utils import ResponseMessageUtils, get_tokens_for_user, extract_first_error_message
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError, AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
import json
from django.contrib.auth import logout
import logging
from .models import OTP
from rest_framework import serializers
from .models import User
import uuid
from rest_framework.exceptions import NotFound

logger = logging.getLogger(__name__)

class SendOTPView(generics.CreateAPIView):
    serializer_class = SendOTPSerializer

    def post(self, request):

        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                result = serializer.save()
                return ResponseMessageUtils(
                    message="OTP Sent to your email",
                    data=result,
                    status_code=status.HTTP_200_OK
                )
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error: {e}")
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class VerifyOTPView(generics.UpdateAPIView):
    queryset = OTP.objects.all()
    serializer_class = VerifyOTPSerializer

    def update(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(message="OTP verified successfully.", status_code=status.HTTP_200_OK)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ResendOTPView(generics.UpdateAPIView):
    queryset = OTP.objects.all()
    serializer_class = ResendOTPSerializer

    def update(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                #access validated data
                result = serializer.save()
                return ResponseMessageUtils(message="Successfully Resend the OTP", data={"otp_token": result.otp_token}, status_code=status.HTTP_200_OK)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
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
            return ResponseMessageUtils(
                message=f"Missing required field: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            

class AddAccountHealthCareProviderView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddAccountHealthCareProviderSerializer

    def post(self, request, *args, **kwargs):
        
        try:
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(message="Added Account Successfully", status_code=status.HTTP_201_CREATED)
            return ResponseMessageUtils(message=serializer.errors["message"][0], status_code=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"ERROR IS: {str(e)}")
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class LoginView(TokenObtainPairView):
    serializer_class = LoginObtainPairSerializer


class RefreshTokenView(TokenRefreshView):

    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):

        try:
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                return ResponseMessageUtils(message="Successfully Refresh your token", data=serializer.data, status_code=status.HTTP_200_OK)
            return ResponseMessageUtils(message=serializer.errors["message"][0], status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ChangePasswordView(generics.UpdateAPIView):
    
    permission_classes = [IsAuthenticated] #must be authenticated to change password

    serializer_class = ChangePasswordSerializer

    def patch(self, request, *args, **kwargs):
        
        auth_header = request.headers.get('Authorization')

        print(f'AUTH HEADER {auth_header}')

        try:
            serializer = self.get_serializer(data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(message="Password updated Successfully", status_code=status.HTTP_200_OK)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ChangePasswordHealthCareProviderView(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated] #must be authenticated to change password

    serializer_class = ChangePasswordHealthCareProviderSeriallizer

    def get_object(self):
        return self.request.user
    
    def patch(self, request, *args, **kwargs):

        try:
            serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(message="Password updated Successfully", status_code=status.HTTP_200_OK)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except AuthenticationFailed as e:
            return ResponseMessageUtils(message="Token has expired or is invalid. Please log in again.", status_code=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetUsersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetUsersSeriaizer
    queryset = User.objects.filter(role='Patient')

class GetUserView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetUserSeriaizer
    queryset = User.objects.all()
    lookup_field = 'id'

    # def get_queryset(self):
    #     return User.objects.all()
    
    # def get_object(self):
        
    #     raw_id = self.kwargs.get('id')

    #     try:
    #         #convert 32-char hex string into UUID object
    #         user_id = uuid.UUID(hex=raw_id)
    #     except ValueError:
    #         raise NotFound("Invalid user ID format")
        
    #     return self.get_queryset().get(id=user_id)


class GetUserRoleView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetUserRoleSerializer
    

    def get(self, request, *args, **kwargs):

        try:
            
            auth_header = request.headers.get('Authorization')

            #check if the authorization is empty or not starts with Bearer
            if not auth_header or not auth_header.startswith('Bearer '):
                return ResponseMessageUtils(message="Authorization is missing or invalid", status_code=status.HTTP_401_UNAUTHORIZED)
            
            #get the token part
            token = auth_header.split(' ')[1]

            try:
                #parse the token
                access_token = AccessToken(token)
            except TokenError as e: 
                return ResponseMessageUtils(message="token is Invalid or expired", status_code=status.HTTP_400_BAD_REQUEST) 

            user = User.objects.get(id=str(access_token["user_id"]))

            serializer = self.get_serializer(user, data=request.data)

            if serializer.is_valid():
                return ResponseMessageUtils(message="Success", data=serializer.data, status_code=status.HTTP_200_OK)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"qwewqe: {str(e)}")
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetHealthCareProvidersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetHealthCareProvidersSerializer

    def get_queryset(self):
        return User.objects.filter(role__in=['Nurse', 'Head Nurse'])

    def get(self, request, *args, **kwargs):

        try:
            user = self.get_queryset()  
            serializer = self.get_serializer(user, many=True)
            return ResponseMessageUtils(message="Success", data=serializer.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            print(f"qwewqe: {str(e)}")
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    



            
