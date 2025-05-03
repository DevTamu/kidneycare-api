from datetime import datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from app_authentication.models import User, OTP
from django.db.models import Q
from .models import Profile, UserInformation
from rest_framework import status
from rest_framework import serializers
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken, TokenError, AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from kidney.utils import generate_otp, send_email_utils, validate_email
import uuid
from django.db import transaction
from django.utils import timezone

class RefreshTokenSerializer(TokenRefreshSerializer):

    token_class = RefreshToken

    def validate(self, attrs):
        #get the refresh token
        refresh_token = attrs.get("refresh")

        #if refresh token is empty
        if not refresh_token:
            raise serializers.ValidationError({"message": "Refresh token is required"})

        try:
            token = RefreshToken(refresh_token)

            #check if the token has expired
            token.check_exp()

            data = super().validate(attrs)

            return {
                "access": data["access"],
                "refresh": data["refresh"]
            }

        except TokenError as e:
            raise serializers.ValidationError({"message": "Token has expired or invalid"})

class SendOTPSerializer(serializers.Serializer):

    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):

        if not value:
            raise serializers.ValidationError({"message": "Email is required"})
        
        if not validate_email(value):
            raise serializers.ValidationError({"message": "Invalid email"})
        
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Email already used")
        
        return value

    def validate_password(self, value):

        if not value:
            raise serializers.ValidationError({"message": "Password is required"})
        
        if len(value) < 8:
            raise serializers.ValidationError({"message": "Password must be atleast 8 characters long."})
        
        return value
        
    def create(self, validated_data):
        
        try:
            #generate an otp
            otp = generate_otp()

            user = User.objects.create_user(
                username=validated_data["username"],
                password=validated_data["password"],
                role="Patient"
            )

            otp_obj = OTP.objects.create(
                user=user,
                otp_code=otp,
                is_verified=False,
                otp_token=uuid.uuid4()
            )

            send_email_utils(
                subject='Your OTP Code',
                message=f'Your OTP is {otp}',
                recipient_list=[f'{validated_data['username']}'],
                otp=otp
            )

            return {
                "otp_token": str(otp_obj.otp_token),
                "user_id": str(user.id)
            }
        except Exception as e:
            return serializers.ValidationError({"message": str(e)})
    

class VerifyOTPSerializer(serializers.Serializer):

    otp_code = serializers.CharField()

    def validate(self, attrs):
        #retrieve the request from the context
        request = self.context.get('request')
        try:
            otp_entry = OTP.objects.get(otp_token=request.query_params.get('otp_token'))
        except OTP.DoesNotExist:
            raise serializers.ValidationError({"message": "Invalid or expired token."})
        #check if the otp valid
        if otp_entry.otp_code != attrs["otp_code"]:
            raise serializers.ValidationError({"message": "Invalid OTP."})
        #check if the otp has expired
        if otp_entry.is_otp_expired():
            raise serializers.ValidationError({"message": "OTP has expired"})
        
        #set the instance to "otp_entry" object for use in "update"
        self.instance = otp_entry

        return attrs
    
    def update(self, instance, validated_data):
        #set the is_verified to True
        instance.is_verified = True
        #save the updated value of is_verified
        instance.save()
        #return the updated instance
        return instance

class ResendOTPSerializer(serializers.Serializer):

    otp_token = serializers.UUIDField()

    def validate(self, attrs):

        try:
            otp_entry = OTP.objects.get(otp_token=attrs["otp_token"])
        except OTP.DoesNotExist:
            raise serializers.ValidationError({"message": "OTP Token does not exist"})
        
        #set the instance to "otp_entry" object for use in "update"
        self.instance = otp_entry

        return attrs


    def update(self, instance, validated_data):
        #generate new otp
        otp = generate_otp()
        #set the new generated otp
        instance.otp_code = otp
        #set new otp token
        instance.otp_token = uuid.uuid4()
        #update the timestamp
        instance.created_at = timezone.now()
        #save the updated otp
        instance.save()
        #return the updated instance
        return instance



class RegisterSerializer(serializers.Serializer):
    
    #user fields (optional)
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    middlename = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    #user fields (required)
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    role = serializers.ChoiceField(allow_blank=True,choices=["Patient", "Admin", "Nurse"], default="Patient")

    # UserInformation fields (optional)
    suffix_name = serializers.BooleanField(required=False)
    birthdate = serializers.DateField(required=False)
    gender = serializers.CharField(required=False)
    contact = serializers.CharField(required=False)

    # Profile field (optional)
    picture = serializers.ImageField(required=False)

    def validate(self, attrs):
        #retrieve the request from the context
        request = self.context.get('request')
        #retrieve the role field in the attrs
        role = attrs["role"]
        
        if role != "Patient":

            #check if username(email) empty
            if not attrs["username"].strip():
                raise serializers.ValidationError({"message": "Email is required"})
            
            #check if password empty
            if not attrs["password"].strip():
                raise serializers.ValidationError({"message": "Password is required"})

            #check the length of the password
            if len(attrs["password"]) < 8:
                raise serializers.ValidationError({"message": "Password must be atleast 8 characters long"})
            
            #check if the email is not a valid email
            if not validate_email(attrs["username"]):
                raise serializers.ValidationError({"message": "Invalid email"})
            
            if not attrs["role"].strip():
                raise serializers.ValidationError({"message": "Role is required"})

        if not attrs["first_name"].strip():
            raise serializers.ValidationError({"message": "Firstname is required"})
        if not attrs["last_name"].strip():
            raise serializers.ValidationError({"message": "Lastname is required"})

        if not attrs["role"].strip():
            raise serializers.ValidationError({"message": "Role is required"})

        #patient required fields
        patient_required_fields = ['middlename', 'birthdate', 'gender', 'contact']

        if role == "Patient":
            #check if patient required fields is empty
            for field in patient_required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError({"message": "This fields is required for patients"})
        elif role in ['Admin', 'Nurse']:
            #remove patient specific fields
            for field in patient_required_fields:
                if field in attrs:
                    attrs.pop(field)
        
        #check the username (username as email) only if the role is ["Admin", "Nurse"]
        if User.objects.filter(username=attrs["username"]).exists() and role in ['Admin', 'Nurse']:
            raise serializers.ValidationError({"message": "Email already used"})

        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        #retrieve the request from the context
        request = self.context.get('request')
        #check if the role is "Patient"
        is_patient = validated_data["role"] == "Patient"
        
        user = None

        if is_patient:
            #retrieve the id param from the request
            id_param = request.query_params.get('id') 
            #check if the id param is empty
            if not id_param:
                raise serializers.ValidationError({"message": "id query parameter is required for Patients"})
            
            #filter user by id (which is set to id_param) and get the first result
            try:
                user = User.objects.filter(id=id_param).first()
            except User.DoesNotExist:
                raise serializers.ValidationError({"message": "User with this id does not exist"})
            
            user.first_name = validated_data["first_name"]
            user.middlename = validated_data["middlename"]
            user.last_name = validated_data["last_name"]
            user.save()
     
            # Create or update User information
            UserInformation.objects.update_or_create(
                user=user,
                defaults={
                    "suffix_name": validated_data.get("suffix_name", False),
                    "birthdate": validated_data.get("birthdate"),
                    "gender": validated_data.get("gender"),
                    "contact": validated_data.get("contact")
                }
            )

        else:
            #for Admin or Nurse, create the user based on validated data
            user = User(
                username=validated_data["username"], 
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                role=validated_data["role"]
            )

            user.set_password(validated_data["password"])
            user.save()

        
        #create the profile (optional) for uploading the picture
        profile = Profile.objects.create(
            user=user,
            picture=validated_data.get("picture")
        )

        return profile

        
class LoginObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):

        request = self.context.get("request")

        username = attrs.get("username")
        password = attrs.get("password")

        try:
            user_role = User.objects.filter(username=username).first()
        except Exception as e:
            raise serializers.ValidationError({"message": "Username does not found"})
        
        if(user_role.role == "Patient"):
            try:
                user_otp = OTP.objects.filter(user__username=username).first()
            except User.DoesNotExist:
                raise serializers.ValidationError({"message": "User does not found"})
        
            if user_otp.user.role == "Patient" and user_otp.is_verified == False:
                raise serializers.ValidationError({"message": "Account verification is required for patients before proceeding."})

        if not username or not password:
            raise serializers.ValidationError({"message": "Both username and password are required"})
        
        user = authenticate(request, username=username, password=password)

        if user is None:
            raise serializers.ValidationError({"message": "Invalid credentials"})
        
        login(request, user)

        try:
            user_profile = Profile.objects.get(user=user)
            picture = request.build_absolute_uri(user_profile.picture.url) if user_profile.picture else None
        except:
            picture = None

        
        # get the current token of the user logged in
        refresh = self.get_token(user)

        data = {
            "message": "Successfully Logged in",
            "data": {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user_id": user.id,
                "user_email": user.username,
                "user_image": picture,
                "user_role": user.role,
            },
            "status": status.HTTP_200_OK
        }

        if user_role.role == "Patient" and user_otp.user.role == "Patient":
            data["data"]["is_verified"] = user_otp.is_verified
        
        return data
    


    @classmethod
    def get_token(self, user):
        token = super().get_token(user)
        #custom claims
        token["username"] = user.username
        token["user_id"] = user.id

        return token
    

class ChangePasswordSerializer(serializers.Serializer):
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        request = self.context.get('request')

        if not attrs["old_password"] or not attrs["new_password"]:
            raise serializers.ValidationError({"message": "Password required"})
        
        if len(attrs["old_password"]) < 8 or len(attrs["new_password"]) < 8:
            raise serializers.ValidationError({"message": "Old and New password must be atleast 8 characters long."})
        
        if not request.user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"message": "Old password don't match"})
        
        return attrs
    
    def update(self, instance, validated_data):
        #set and hash new password
        instance.set_password(validated_data["new_password"])
        #save the updated user instance
        instance.save()
        #return the updated user instance
        return instance
    

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.refresh_token = attrs['refresh']

        request = self.context.get('request')
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            raise serializers.ValidationError({"message": 'No valid Authorization header found.'})   
        
        self.access_token_str = auth_header.split(' ')[1]  # Get the token part

        return attrs

    def save(self, **kwargs):
        
        try:
            # Blacklist refresh token
            refresh_token = RefreshToken(self.refresh_token)
            refresh_token.blacklist()
        except TokenError:
            raise serializers.ValidationError({"message": "Invalid refresh token."})

        try:
            #blacklist access token
            access_token = AccessToken(self.access_token_str)

            # Ensure datetime fields are correctly formatted as strings
            created_at_str = datetime.fromtimestamp(access_token['iat']).isoformat()
            expires_at_str = datetime.fromtimestamp(access_token['exp']).isoformat()

            # Create OutstandingToken if not exists
            outstanding_token, _ = OutstandingToken.objects.get_or_create(
                jti=access_token['jti'],
                defaults={
                    'user_id': self.context['request'].user.id,
                    'token': str(access_token),
                    'created_at': created_at_str,
                    'expires_at': expires_at_str,
                }
            )

            # Blacklist the access_token
            BlacklistedToken.objects.get_or_create(token=outstanding_token)
        except TokenError as e:
            raise serializers.ValidationError({"message": "Invalid access token."})
        except Exception as e:
            raise serializers.ValidationError({"message": "Error occured during logout"})

            




            

