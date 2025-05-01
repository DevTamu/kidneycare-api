from .serializers import (
    RegisterSerializer,
    LoginObtainPairSerializer,
    RefreshTokenSerializer,
    ChangePasswordSerializer,
    CustomLogoutTokenBlacklistSerializer
)
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import AccessToken
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
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

logger = logging.getLogger(__name__)

# class IsNotBlacklisted(BasePermission):
#     def has_permission(self, request, view):
#         try:
#             #get the token from the authorization header
#             auth_header = request.META.get('HTTP_AUTHORIZATION', '')

#             if not auth_header:
#                 return False
            
#             parts = auth_header.split()
#             if len(parts) != 2 or parts[0].lower() != 'bearer':
#                 return False
            
#             # Decode the token without verification first to get jti
#             token = AccessToken(parts[1])
#             jti = token.payload.get('jti')

#             # Check if this token is blacklisted
#             return not BlacklistedToken.objects.filter(token__jti=jti).exists()
#         except TokenError as e:
#             return False
#         except Exception as e:
#             logger.error(f"Error: {str(e)}")
#             return False

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
        
            return ResponseMessageUtils(
                message=serializer.errors["message"][0],
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return ResponseMessageUtils(
                message=f"Something went wrong: {str(e)}",
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
    serializer_class = CustomLogoutTokenBlacklistSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        try:
            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(message="Successfully logged out", status_code=status.HTTP_200_OK) 
            return ResponseMessageUtils(message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            return ResponseMessageUtils(message="Error Occured during logout", status_code=status.HTTP_400_BAD_REQUEST) 
