from .serializers import (
    RegisterSerializer,
    RegisterAdminSerializer,
    LoginObtainPairSerializer,
    WebLoginObtainPairSerializer,
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
    GetHealthCareProvidersSerializer,
    EditProfileInPatientSerializer,
    GetProfileProfileInPatientSerializer,
    GetAllRegisteredProvidersSerializer,
    RegisterCaregiverSerializer,
    CaregiverListSerializer,
)
from kidney.pagination.appointment_pagination import Pagination
from rest_framework import serializers
from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics
from kidney.utils import ResponseMessageUtils, get_tokens_for_user, extract_first_error_message, get_token_user_id
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import logout
from .models import OTP, User, Profile, UserInformation, Caregiver
from django.http import JsonResponse
from kidney.pagination.appointment_pagination import Pagination
from kidney.permissions import IsAdmin, IsProvider, IsPatient, IsCaregiver

def ping(request):
    return JsonResponse({"status": "ok"})

class SendOTPView(generics.CreateAPIView):

    serializer_class = SendOTPSerializer

    def post(self, request):

        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                result = serializer.save()
                return ResponseMessageUtils(
                    message="Please verifiy your account" if result.get('is_verified') == "Unverified" else "Your OTP code has been sent to your gmail",
                    data=result,
                    status_code=status.HTTP_200_OK
                )
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class VerifyOTPView(generics.UpdateAPIView):

    serializer_class = VerifyOTPSerializer
    queryset = OTP.objects.all()

    def update(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                result = serializer.save()
                return ResponseMessageUtils(
                    message="Account verified successfully, you may now log in.",
                    data={'user_id': str(result.user.id)},
                    status_code=status.HTTP_200_OK
                )
            return ResponseMessageUtils(
                message=extract_first_error_message(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ResendOTPView(generics.UpdateAPIView):

    serializer_class = ResendOTPSerializer
    queryset = OTP.objects.all()

    def update(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                result = serializer.save()
                return ResponseMessageUtils(
                    message="Successfully Resend the OTP",
                    data={"otp_token": result.otp_token},
                    status_code=status.HTTP_200_OK
                )
            return ResponseMessageUtils(
                message=extract_first_error_message(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer

    def post(self, request):

        try:
            user_information = None
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                #save the data
                user_profile = serializer.save()
                user = user_profile.user
                try:
                    user_information = UserInformation.objects.get(user=user)
                except UserInformation.DoesNotExist:
                    pass
                token = get_tokens_for_user(user)

                return ResponseMessageUtils(
                    message="Account Registered Successfully",
                    data={
                        "access_token": token["access_token"],
                        "refresh_token": token["refresh_token"],
                        "user_id": str(user.id),
                        "user_email": user.username,
                        "first_name": user.first_name,
                        "middle_name": user.middlename if user.middlename else None,
                        "last_name": user.last_name,
                        "user_image": request.build_absolute_uri(user_profile.picture.url) if user_profile.picture else None,
                        "user_role": str(user.role).lower(),
                        "birth_date": user_information.birthdate.strftime('%m/%d/%Y') if user_information.birthdate else None,
                        "gender": user_information.gender.lower(),
                        "contact_number":  user_information.contact,
                        "is_online": str(user.status).lower()
                    },
                    status_code=status.HTTP_201_CREATED
                )
            return ResponseMessageUtils(
                message=extract_first_error_message(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class RegisterAdminView(generics.CreateAPIView):

    serializer_class = RegisterAdminSerializer

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
                        "access_token": token["access_token"],
                        "refresh_token": token["refresh_token"],
                        "user_id": str(user.id),
                        "user_email": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "user_image": request.build_absolute_uri(user_profile.picture.url) if user_profile.picture else None,
                        "user_role": str(user.role).lower(),
                        "user_status": str(user.status).lower()
                    },
                    status_code=status.HTTP_201_CREATED
                )
            return ResponseMessageUtils(
                message=extract_first_error_message(serializer.errors),
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
                return ResponseMessageUtils(
                    message="Added Account Successfully",
                    status_code=status.HTTP_201_CREATED
                )
            return ResponseMessageUtils(
                message=extract_first_error_message(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(TokenObtainPairView):
    serializer_class = LoginObtainPairSerializer

class LoginWebView(TokenObtainPairView):
    serializer_class = WebLoginObtainPairSerializer


class RefreshTokenView(TokenRefreshView):

    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):

        try:
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                return ResponseMessageUtils(
                    message="Successfully Refresh your token",
                    data=serializer.data,
                    status_code=status.HTTP_200_OK
                )
            return ResponseMessageUtils(
                message=extract_first_error_message(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ChangePasswordView(generics.UpdateAPIView):
    
    permission_classes = [IsAuthenticated]

    serializer_class = ChangePasswordSerializer

    def patch(self, request, *args, **kwargs):
        
        try:

            serializer = self.get_serializer(data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(
                    message="Password updated Successfully",
                    status_code=status.HTTP_200_OK
                )
            return ResponseMessageUtils(
                message=extract_first_error_message(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(generics.CreateAPIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        try:
            if serializer.is_valid():
                serializer.save()
                logout(request)
                return ResponseMessageUtils(
                    message="Successfully logged out",
                    status_code=status.HTTP_200_OK
                ) 
            return ResponseMessageUtils(
                message=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            ) 
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
                return ResponseMessageUtils(
                    message="Password updated Successfully",
                    status_code=status.HTTP_200_OK
                )
            return ResponseMessageUtils(
                message=extract_first_error_message(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except AuthenticationFailed as e:
            return ResponseMessageUtils(
                message="Token has expired or is invalid. Please log in again.",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetUsersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetUsersSeriaizer
    pagination_class = Pagination
    
    def get(self, request, *args, **kwargs):

        try:
            user = User.objects.filter(role='patient')
            paginator = self.pagination_class()
            paginated_data = paginator.paginate_queryset(user, request)
            serializer = self.get_serializer(paginated_data, many=True, context={'request': request})
            paginated_response = paginator.get_paginated_response(serializer.data)
            return ResponseMessageUtils(
                message="List of Patients",
                data=paginated_response.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetUserView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetUserSeriaizer
    queryset = User.objects.all()
    lookup_field = 'pk'


class GetUserRoleView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetUserRoleSerializer
    

    def get(self, request, *args, **kwargs):

        try:
            
            user_id = get_token_user_id(request)

            user = User.objects.get(id=user_id)

            serializer = self.get_serializer(user, data=request.data)

            if serializer.is_valid():
                return ResponseMessageUtils(message="Success", data=serializer.data, status_code=status.HTTP_200_OK)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# import traceback
class GetHealthCareProvidersView(generics.ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = GetHealthCareProvidersSerializer
    pagination_class = Pagination

    def get_queryset(self):
        return User.objects.filter(role__in=['nurse', 'head nurse'])

    def get(self, request, *args, **kwargs):

        try:
            user = self.get_queryset()  

            paginator = self.pagination_class()

            paginated_data = paginator.paginate_queryset(user, request)

            serializer = self.get_serializer(paginated_data, many=True)

            paginated_response = paginator.get_paginated_response(serializer.data)

            return ResponseMessageUtils(
                message="List of Providers",
                data=paginated_response.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            # traceback.print_exc()
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    
class EditProfileInPatientView(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = EditProfileInPatientSerializer
    
    def patch(self, request, *args, **kwargs):

        try:
            #get the current authenticated user id
            user_id = get_token_user_id(request)
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return ResponseMessageUtils(
                    message="User not found.",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Get or create related objects
            user_information, _ = UserInformation.objects.get_or_create(user=user)
            user_profile, _ = Profile.objects.get_or_create(user=user)
          

            # Update user fields if present in data
            user.first_name = request.data.get('first_name', user.first_name)
            user.middlename = request.data.get('middle_name', user.middlename)
            user.last_name = request.data.get('last_name', user.last_name)
            user.save()

            birth_date = request.data.get('birth_date', None)
            if birth_date:
                date_field = serializers.DateField(input_formats=['%m/%d/%Y'])
                try:
                    birth_date_obj = date_field.to_internal_value(birth_date)
                except serializers.ValidationError:
                    birth_date_obj = None
                if birth_date_obj:
                    user_information.birthdate = birth_date_obj
            else:
                # If no birth_date provided in data, keep existing value
                user_information.birthdate = user_information.birthdate

            user_information.gender = request.data.get('gender', user_information.gender)
            user_information.contact = request.data.get('contact_number', user_information.contact)
            user_information.save()

            user_profile = Profile.objects.get(user_id=user_id)

            serializer = self.get_serializer(instance=user_profile, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                #refresh from the database to get updated values
                user.refresh_from_db()
                user_information.refresh_from_db()
                user_profile.refresh_from_db()

                return ResponseMessageUtils(message="Successfully updated your profile", data={
                    "first_name": user.first_name,
                    "middle_name": user.middlename,
                    "last_name": user.last_name,
                    "birth_date": user_information.birthdate.strftime('%m/%d/%Y'),
                    "gender": str(user_information.gender).lower(),
                    "contact_number": user_information.contact,
                    "user_image": request.build_absolute_uri(user_profile.picture.url) if user_profile.picture else None
                }, status_code=status.HTTP_200_OK)
            
                # return ResponseMessageUtils(message="Successfully updated your profile", status_code=status.HTTP_200_OK)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetUserProfileInformationView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetProfileProfileInPatientSerializer

    def get(self, request, *args, **kwargs):

        try:
            #get the user id
            user_id = get_token_user_id(request)

            user_profile = Profile.objects.get(user_id=user_id)
            
            serializer = self.get_serializer(user_profile)
            return ResponseMessageUtils(
                message="Profile Information",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Profile.DoesNotExist:
            return ResponseMessageUtils(
                message="No Profile information found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetAllRegisteredProvidersView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetAllRegisteredProvidersSerializer
    
    def get(self, request, *args, **kwargs):

        try:

            # data_cache_key = 'all_registered_providers'

            # #check if data is already in cache
            # cached_data = cache.get(data_cache_key)
            # if cached_data is not None:
            #     return ResponseMessageUtils(
            #         message="List of registered providers",
            #         data=cached_data,
            #         status_code=status.HTTP_200_OK
            #     )

            queryset = User.objects.filter(role__in=['nurse', 'head nurse'])
            serializer = self.get_serializer(queryset, many=True)

            # # cache the serialized data for 10 minutes (600 seconds)
            # cache.set(data_cache_key, serializer.data, timeout=600)

            return ResponseMessageUtils(
                message="List of registered providers",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class RegisterCaregiverSerializer(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = RegisterCaregiverSerializer
        
    def post(self, request, *args, **kwargs):

        try:

            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(
                    message="Account created successfully",
                    status_code=status.HTTP_201_CREATED
                )
            return ResponseMessageUtils(
                message=extract_first_error_message(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            print(f"WHAT WENT WRONG? {e}")
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class CaregiverListView(generics.RetrieveDestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = CaregiverListSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        user_id = get_token_user_id(self.request)
        return Caregiver.objects.filter(added_by=user_id)
    
    def get_object(self):
        return Caregiver.objects.filter(id=self.kwargs.get('pk')).first()

    def destroy(self, request, *args, **kwargs):
        
        try:

            instance = self.get_object()

            if not instance:
                return ResponseMessageUtils(
                message="No caregiver found",
                status_code=status.HTTP_404_NOT_FOUND
            )

            instance.user.delete()

            return ResponseMessageUtils(
                message="Successfully deleted",
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )   

    def get(self, request, *args, **kwargs):

        try:

            queryset = self.get_queryset()

            if not queryset.exists():
                return ResponseMessageUtils(
                    message="No caregiver found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.get_serializer(queryset, many=True)

            return ResponseMessageUtils(
                message="List of caregivers",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

