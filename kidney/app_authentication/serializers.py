from datetime import datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from app_authentication.models import User, OTP
from django.db.models import Q
from .models import Profile, UserInformation, User
from rest_framework import status
from rest_framework import serializers
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken, TokenError, AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from kidney.utils import generate_otp, send_otp_to_email, send_password_to_email, validate_email, is_field_empty, generate_password
import uuid
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

OTP_VALIDITY_SECONDS = 180  # 3 minutes

class RefreshTokenSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        #get the refresh token
        refresh_token = attrs.get("refresh")

        #if refresh token is empty
        if not refresh_token:
            raise serializers.ValidationError({"message": "Refresh token is required"})

        try:
            
            data = super().validate(attrs)

            return {
                "access": data["access"],
                "refresh": refresh_token
            }

        except TokenError as e:
            raise serializers.ValidationError({"message": "Token has expired or invalid"})
        


class SendOTPSerializer(serializers.Serializer):

    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        username = attrs["username"]
        password = attrs["password"]

        #fields validations
        if is_field_empty(username):
            raise serializers.ValidationError({"message": "Email is required"})
        
        if not validate_email(username):
            raise serializers.ValidationError({"message": "Must be a valid email address"})
        
        # if OTP.objects.filter(user__username=username).exists():
        #     raise serializers.ValidationError("Email already used")

        if is_field_empty(password):
            raise serializers.ValidationError({"message": "Password is required"})
        
        if len(password) < 8:
            raise serializers.ValidationError({"message": "Password must be atleast 8 characters long."})
        
        return attrs
        
    def create(self, validated_data):
        
        try:

            existing_user = User.objects.filter(username=validated_data["username"]).first()

            #check if there's an existing OTP object for an unverified user
            if existing_user:
                otp_obj = OTP.objects.filter(user=existing_user, is_verified=False).first()

                if otp_obj:
                    
                    now = timezone.now()
                    #elapsed time that has passed after the first creation of the account
                    elapsed_time = (now - otp_obj.created_at).total_seconds()
                    #calculate the remaining time
                    remaining_time = max(0, OTP_VALIDITY_SECONDS - int(elapsed_time))
                    return {
                        "is_verified": "Unverified",
                        "otp_token": str(otp_obj.otp_token).replace("-", ""),
                        "timer": remaining_time
                    }
                else:
                    raise serializers.ValidationError({"message": "Email already used"})

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

            send_otp_to_email(
                subject='Your OTP Code',
                message=f'Your OTP is {otp}',
                recipient_list=[user.username],
                otp=otp_obj.otp_code
            )

            return {
                "otp_token": str(otp_obj.otp_token).replace("-", ""),
                "timer": int(timedelta(minutes=3).total_seconds())
            }
        
        except Exception as e:
            raise serializers.ValidationError({"message": str(e)})
        

class VerifyOTPSerializer(serializers.Serializer):

    otp_code = serializers.CharField(write_only=True)

    def validate(self, attrs):

        #get the request object from the serializer context
        request = self.context.get('request')

        if is_field_empty(attrs["otp_code"]):
            raise serializers.ValidationError({"message": "OTP is required"})

        otp = OTP.objects.get(otp_token=request.headers.get('X-OTP-Token'))

        if not otp:
            raise serializers.ValidationError({"message": "Invalid otp token"})
        
        if otp.is_verified:
            raise serializers.ValidationError({"message": "This account has already been verified"})
           
        #check if the otp valid
        if otp.otp_code != attrs["otp_code"]:
            raise serializers.ValidationError({"message": "Invalid OTP."})
        
        #check if the otp has expired
        if otp.is_otp_expired():
            raise serializers.ValidationError({"message": "OTP has expired"})
        
        #set the instance to "otp" object for use in "update"
        self.instance = otp

        return attrs
    
    def update(self, instance, validated_data):
        #set the is_verified to True
        instance.is_verified = True
        #save the updated value of is_verified
        instance.save()
        #return the updated instance
        return instance

class ResendOTPSerializer(serializers.Serializer):

    otp_token = serializers.CharField(error_messages={'blank': 'OTP TOKEN is required'})

    def validate(self, attrs):

        if is_field_empty(str(attrs["otp_token"])):
            raise serializers.ValidationError({"message": "OTP TOKEN is required"})

        try:
            otp_token = OTP.objects.get(otp_token=attrs["otp_token"])
        except OTP.DoesNotExist:
            raise serializers.ValidationError({"message": "OTP Token does not exist"})
        
        if otp_token.is_verified:
            raise serializers.ValidationError({"message": "This account has already been verified"})   

        #set the instance to "otp_token" object for use in "update"
        self.instance = otp_token

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
        #send otp to email
        send_otp_to_email(
            subject='Your OTP Code',
            message=f'Your OTP is {otp}',
            recipient_list=[f'{instance.user.username}'],
            otp=otp
        )
        #return the updated instance
        return instance


class AddAccountHealthCareProviderSerializer(serializers.Serializer):
    
    #required fields
    username = serializers.CharField(allow_blank=True, allow_null=True)
    firstname = serializers.CharField(allow_blank=True, allow_null=True)
    lastname = serializers.CharField(allow_blank=True, allow_null=True)
    role = serializers.CharField(allow_blank=True, allow_null=True)
    contact_number = serializers.CharField(allow_blank=True, allow_null=True)
    address = serializers.CharField(allow_blank=True, allow_null=True)  
    
    #optional field
    picture = serializers.ImageField(required=False)

    def validate(self, attrs):

        required_fields = ['firstname', 'lastname', 'address', 'role']

        if is_field_empty(attrs["username"]):
            raise serializers.ValidationError({"message": "Email is required"})
                
        if is_field_empty(attrs["contact_number"]):
            raise serializers.ValidationError({"message": "Contact number is require"})

        #check for all the required fields if (empty)
        for field in required_fields:

            if is_field_empty(attrs.get(field)):
                raise serializers.ValidationError({"message": f"{field} is required"})
        
        #check if its a valid email address
        if not validate_email(attrs["username"]):
            raise serializers.ValidationError({"message": "Must be a valid email address"})
        
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError({"message": "Email already used"})
            
        return attrs
    
    #add transaction atomic to ensure the data will rollback in case of failure 
    @transaction.atomic
    def create(self, validated_data):
        
        #generate password
        generated_password = generate_password()

        #create user
        user = User.objects.create_user(
            username=validated_data["username"],
            password=generated_password,
            first_name=validated_data["firstname"],
            last_name=validated_data["lastname"],
            role=validated_data["role"]
        )

        #create related user information
        UserInformation.objects.create(
            user=user,
            contact=validated_data["contact_number"],
            address=validated_data["address"]
        )

        #create profile
        picture = validated_data.get('picture', None)
        user_profile = Profile.objects.create(
            user=user,
            picture=picture
        )

        #send password to the gmail
        send_password_to_email(
            subject='Generated Password',
            message=f'Your Password is {generated_password}',
            recipient_list=[f'{validated_data['username']}'],
            password=generated_password
        )
        
        return user_profile
        


class RegisterSerializer(serializers.Serializer):
    
    #user fields (optional)
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    middlename = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    #user fields (required)
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    role = serializers.CharField(allow_blank=True)

    # UserInformation fields (optional)
    birthdate = serializers.DateField(required=False)
    gender = serializers.CharField(required=False)
    contact = serializers.CharField(required=False)
    age = serializers.CharField(required=False)

    # Profile field (optional)
    picture = serializers.ImageField(required=False)

    def validate(self, attrs):

        #get the request from the context
        request = self.context.get('request')
        #retrieve the role field in the attrs
        role = attrs["role"]
        
        if role != "Patient":

            #check if username(email) empty
            if is_field_empty(attrs["username"]):
                raise serializers.ValidationError({"message": "Email is required"})
            
            #check if password empty
            if is_field_empty(attrs["password"]):
                raise serializers.ValidationError({"message": "Password is required"})

            #check the length of the password
            if len(attrs["password"]) < 8:
                raise serializers.ValidationError({"message": "Password must be atleast 8 characters long"})
            
            #check if the email is not a valid email
            if not validate_email(attrs["username"]):
                raise serializers.ValidationError({"message": "Must be a valid email address"})
            
            if is_field_empty(attrs["role"]):
                raise serializers.ValidationError({"message": "Role is required"})

        if is_field_empty(attrs["first_name"]):
            raise serializers.ValidationError({"message": "Firstname is required"})
        if is_field_empty(attrs["last_name"]):
            raise serializers.ValidationError({"message": "Lastname is required"})

        if is_field_empty(attrs["role"]):
            raise serializers.ValidationError({"message": "Role is required"})

        #patient required fields
        patient_required_fields = ['middlename', 'birthdate', 'gender', 'contact', 'age']

        if role == "Patient":
            #check if patient required fields is empty
            for field in patient_required_fields:
                if is_field_empty(attrs.get(field)):
                    raise serializers.ValidationError({"message": "This fields is required for patients"})
        elif role == 'Admin':
            #remove patient specific fields
            for field in patient_required_fields:
                if field in attrs:
                    attrs.pop(field)
        
        #check the username (username as email) only if the role is 'Admin'
        if User.objects.filter(username=attrs["username"]).exists() and role == 'Admin':
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
            if is_field_empty(id_param):
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
                    # "suffix_name": validated_data.get("suffix_name", False),
                    "birthdate": validated_data.get("birthdate"),
                    "gender": validated_data.get("gender"),
                    "contact": validated_data.get("contact"),
                    "age": validated_data.get('age')
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
        #set the is_verified default to None
        self.is_verified = None
        #get the request object from the serializer context
        request = self.context.get("request")
        #login fields
        username = attrs.get("username")
        password = attrs.get("password")

        if is_field_empty(username) or is_field_empty(password):
            raise serializers.ValidationError({"message": "Both username and password are required"})

        user = User.objects.filter(username=username).first()
        
        if not user:
            raise serializers.ValidationError({"message": "Username does not exist"})

        #OTP Verification (applicable only for PATIENT role)
        if user.role == 'Patient':
            otp = OTP.objects.filter(user__username=username).first()
            if not otp:
                raise serializers.ValidationError({"message": "OTP not found"})
            if not otp.is_verified:
                raise serializers.ValidationError({"message": f"{otp.user.role} account verification is required before proceeding."})
            else:
                self.is_verified = otp.is_verified
            
        
        user = authenticate(request, username=username, password=password)

        #if no user found
        if user is None:
            raise serializers.ValidationError({"message": "Invalid credentials"})
        

        login(request, user)

        #generate token
        refresh = self.get_token(user)

        try:
            user_profile = Profile.objects.get(user=user)
            user.status = 'Online'
            user.save()
            picture = request.build_absolute_uri(user_profile.picture.url) if user_profile.picture else None
        except Profile.DoesNotExist:
            picture = None

       
        data =  {
            "message": "Successfully Logged in",
            "data": {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user_id": str(user.id).replace("-", ""),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_email": user.username,
                "user_image": picture,
                "user_role": user.role,
                "user_status": user_profile.user.status
            },
        }

        if user.role == 'Patient':
            data["data"]["is_verified"] = self.is_verified
        else:
            pass

        return data
    
    @classmethod
    def get_token(self, user):
        token = super().get_token(user)
        #custom claims
        token["username"] = user.username

        return token
    

class ChangePasswordSerializer(serializers.Serializer):
    
    old_password = serializers.CharField(
        write_only=True,
        error_messages={'blank': 'Old password cannot be blank'}
    )
    new_password = serializers.CharField(
        write_only=True,
        error_messages={'blank': 'New password cannot be blank'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        error_messages={'blank': 'Confirm password cannot be blank'}
    )

    def validate(self, attrs):

        request = self.context.get('request')

        if is_field_empty(attrs["old_password"]):
            raise serializers.ValidationError({"message": "Old password is required"})

        if is_field_empty(attrs["new_password"]):
            raise serializers.ValidationError({"message": "New password is required"})

        if is_field_empty(attrs["confirm_password"]):
            raise serializers.ValidationError({"message": "Confirm password is required"})
        
        if not request.user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"message": "Old password don't match"})
        
        if len(attrs["confirm_password"]) < 8 or len(attrs["new_password"]) < 8:
            raise serializers.ValidationError({"message": "New password and Confirm password must be atleast 8 characters long"})
        
        if attrs["confirm_password"] != attrs["new_password"]:
            raise serializers.ValidationError({"message": "New password and Confirm password don't match"})

        #set the instance to the current user for use in the update method
        self.instance = request.user

        return attrs
    
    def update(self, instance, validated_data):
        #set and hash new password
        instance.set_password(validated_data["new_password"])
        #save the user instance
        instance.save()
        #return the updated user instance
        return instance
    

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.refresh_token = attrs['refresh']
        #get the request from the context
        request = self.context.get('request')
        #get the authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            raise serializers.ValidationError({"message": 'No valid Authorization header found.'})   
        
        #get the token part
        self.access_token_str = auth_header.split(' ')[1]

        return attrs

    def save(self, **kwargs):
        
        try:
            # Blacklist refresh token
            refresh_token = RefreshToken(self.refresh_token)
            refresh_token.blacklist()
        except TokenError:
            raise serializers.ValidationError({"message": "Invalid refresh token."})

        try:

            access_token = AccessToken(self.access_token_str)

            user = User.objects.get(id=access_token["user_id"])

            if not user:
                raise serializers.ValidationError({"message": "No user found"})
                            
            user.status = 'Offline'
            user.save()

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

            
class ChangePasswordHealthCareProviderSeriallizer(serializers.Serializer):

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        #get the request from the context
        request = self.context.get('request')

        if is_field_empty(attrs["old_password"]) or is_field_empty(attrs["new_password"]):
            raise serializers.ValidationError({"message": "Password must not be empty"})
        
        if len(attrs["old_password"]) < 8 or len(attrs["new_password"]) < 8:
            raise serializers.ValidationError({"message": "Password must be atleast 8 characters long"})
        
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

            
class GetUsersInformationSerializer(serializers.ModelSerializer):

    #format the birthdate to readable format
    birthdate = serializers.DateField(format='%b %d, %Y', input_formats=['%b %d, $Y'])

    class Meta:
        model = UserInformation
        fields = '__all__'


    def to_representation(self, instance):
        data = super().to_representation(instance)

        data.pop('created_at')
        data.pop('updated_at')

        data.pop('user')

        # data.pop('suffix_name')
        data.pop('address')

        return data

class GetUsersSeriaizer(serializers.ModelSerializer):

    picture = serializers.SerializerMethodField()
    user_information = GetUsersInformationSerializer()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'id', 'picture', 'user_information']


    def to_representation(self, instance):
        data = super().to_representation(instance)

        #rename keys
        data["user_id"] = str(data.pop('id')).replace("-", "")

        #default keys from user_information
        default_user_info = {
            "birthdate": None,
            "gender": None,
            "contact": None,
            "age": None
        }

        user_information = data.pop('user_information', {}) or {}

        #merge with defaults to ensure all keys are present
        full_user_info = {**default_user_info, **user_information}

        data.update(full_user_info)
        
        return data


    def get_picture(self, obj):

        #get the request object from the serializer context
        request = self.context.get('request')

        profile = getattr(obj, 'user_profile', None)

        #check if the user profile exist and the profile picture
        if profile and profile.picture:
            return request.build_absolute_uri(profile.picture.url) if profile.picture else None
        return None


class GetUserSeriaizer(serializers.ModelSerializer):

    picture = serializers.SerializerMethodField()
    user_information = GetUsersInformationSerializer()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'id', 'picture', 'user_information']


    def to_representation(self, instance):
        data = super().to_representation(instance)

        #rename keys
        data["user_id"] = str(data.pop('id')).replace("-", "")
        
        #default keys from user_information
        default_user_info = {
            "birthdate": None,
            "gender": None,
            "contact": None,
            "age": None
        }

        user_information = data.pop('user_information', {}) or {}

        #merge with defaults to ensure all keys are present
        full_user_info = {**default_user_info, **user_information}

        data.update(full_user_info)
        
        return data

    def get_picture(self, obj):

        #get the request from the context
        request = self.context.get('request')

        if obj.user_profile and obj.user_profile.picture:
            return request.build_absolute_uri(obj.user_profile.picture.url) if obj.user_profile.picture else None
        return None
    
class GetUserRoleSerializer(serializers.ModelSerializer):

    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['role']


    def to_representation(self, instance):
        data = super().to_representation(instance)

        #rename key
        data["user_role"] = data.pop('role')

        return data
    

class GetProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields = ['picture']


class GetUserInformationSerializer(serializers.ModelSerializer):


    class Meta:
        model = UserInformation
        fields = ['address', 'contact']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #formatting the contact with hyphens
        data["contact"] = '{}{}{}{}-{}{}{}-{}{}{}{}'.format(*data.pop('contact'))

        return data
    

class GetHealthCareProvidersSerializer(serializers.ModelSerializer):

    user_profile = GetProfileSerializer()
    user_information = GetUserInformationSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role', 'user_profile', 'user_information']

    def to_representation(self, instance):

        data = super().to_representation(instance)

        #flatten user_information into the main data response
        user_info = data.pop('user_information', {})
        data.update(user_info)

        #flatten user profile into the main data response
        user_profile = data.pop('user_profile', {})
        data.update(user_profile)

        #rename keys
        data["contact_number"] = data.pop('contact', None)
        data["user_id"] = str(data.pop('id')).replace("-", "")

        return data


class EditProfileInPatientSerializer(serializers.Serializer):

    #optional field
    picture = serializers.ImageField(required=False)
    
    #user fields inputs
    first_name = serializers.CharField(write_only=True, allow_null=True, allow_blank=True, error_messages={"blank": "This field is required"})
    middle_name = serializers.CharField(write_only=True, allow_null=True, allow_blank=True, error_messages={"blank": "This field is required"})
    last_name = serializers.CharField(write_only=True, allow_null=True, allow_blank=True, error_messages={"blank": "This field is required"})
    
    #user information inputs
    birth_date = serializers.DateField(format='%m/%d/%Y', input_formats=['%m/%d/%Y'])
    gender = serializers.CharField(write_only=True, allow_null=True, allow_blank=True, error_messages={"blank": "This field is required"})
    contact_number = serializers.CharField(write_only=True, allow_null=True, allow_blank=True, error_messages={"blank": "This field is required"})

    def validate(self, attrs):

        required_fields = ['first_name', 'last_name', 'birth_date', 'gender', 'contact_number']

        for field in required_fields:
            if is_field_empty(attrs.get(field)):
                raise serializers.ValidationError({"message": "All fields are required"})

        return attrs        

    def update(self, instance, validated_data):
        

        picture = validated_data.get('picture', None)
        if picture:
            instance.picture = picture
        
        #user instance object
        user = instance.user

        user.first_name = validated_data.get('first_name', None)
        user.middlename = validated_data.get('middle_name', None)
        user.last_name = validated_data.get('last_name', None)

        #save the user object
        user.save()

        #user information instance object
        user_information = instance.user.user_information
        user_information.birthdate = validated_data.get('birth_date', None)
        user_information.gender = validated_data.get('gender', None)
        user_information.contact = validated_data.get('contact_number', None)

        #save the user information object
        user_information.save()
        
        #save the profile object
        instance.save()

        return instance

class GetProfileProfileInPatientSerializer(serializers.ModelSerializer):


    class Meta:
        model = Profile
        fields = ['picture', 'user']

    def to_representation(self, instance):

        data = super().to_representation(instance)

        try:
            user_information = UserInformation.objects.select_related('user').get(user=data["user"])
        except Exception as e:
            pass
        
        #user informations
        data["first_name"] = user_information.user.first_name
        data["middle_name"] = user_information.user.middlename if user_information.user.middlename else None
        data["last_name"] = user_information.user.last_name
        data["birth_date"] = user_information.birthdate
        data["gender"] = user_information.gender
        data["contact_number"] = user_information.contact

        return data
    

class AutomaticDeleteUnverifiedUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'is_verified', 'created_at']