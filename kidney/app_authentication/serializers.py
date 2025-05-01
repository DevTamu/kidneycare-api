from datetime import datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer, TokenBlacklistSerializer
from app_authentication.models import User
from django.db.models import Q
from .models import Profile, UserInformation
from rest_framework import status
from rest_framework import serializers
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken, TokenError, AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

class RefreshTokenSerializer(TokenRefreshSerializer):

    token_class = RefreshToken

    def validate(self, attrs):
        #get the refresh token
        refresh_token = attrs.get("refresh")

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


class RegisterSerializer(serializers.Serializer):
    
     # User fields (required)
    username = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=["Patient", "Admin", "Nurse"],
        default="Patient"
    )

    # UserInformation fields (optional)
    suffix_name = serializers.CharField(required=False)
    birthdate = serializers.DateField(required=False)
    gender = serializers.CharField(required=False)

    # Profile field (optional)
    picture = serializers.ImageField(required=False)

    def validate(self, attrs):
        
        required_fields = ["username", "first_name", "last_name", "password", "role"]
        #check required fields(empty)
        for field in required_fields:
            if not attrs.get(field):
                raise serializers.ValidationError({"message": f"{field} is required"})

        #check if username (email) already exists
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError({"message": "Email already exists"})
        
        #password validation
        if len(attrs["password"]) < 8 or len(attrs["confirm_password"]) < 8:
            raise serializers.ValidationError({"message": "Password must be atleast 8 characters long."})

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"message": "Password don't match"})
        
        return attrs
    

    def create(self, validated_data):

        # Remove confirm_password
        validated_data.pop('confirm_password')

        #create the user
        user = User.objects.create_user(
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
            role=validated_data["role"] #Default to patient
        )

        #only create user information for patients
        if validated_data.get("role") == "Patient":
            user_info_data = {
                'suffix_name': validated_data.get('suffix_name'),
                'birthdate': validated_data.get('birthdate'),
                'gender': validated_data.get('gender')
            }
            # create the user information
            UserInformation.objects.create(user=user,**user_info_data)

        #create the profile
        profile = Profile.objects.create(
            user=user,
            picture=validated_data.get("picture")
        )

        return profile
    


class LoginObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):

        request = self.context.get("request")

        email = attrs.get(self.username_field)
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError({"message": "Both email and password are required"})
        
        user = authenticate(request, username=email, password=password)

        if user is None:
            raise serializers.ValidationError({"message": "Invalid credentials"})
        
        login(request, user)

        try:
            user_profile = Profile.objects.get(user_id=user)
            picture = request.build_absolute_uri(user_profile.picture.url) if user_profile.picture else None
        except Profile.DoesNotExist:
            raise serializers.ValidationError({"message": "User Profile does not exists"})
        
        # get the current token of the user logged in
        refresh = self.get_token(user)

        return {
            "message": "Successfully Logged in",
            "data": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": user_profile.user.id,
                "user_email": user_profile.user.username,
                "user_image": picture
            },
            "status": status.HTTP_200_OK
        }


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
    

class CustomLogoutTokenBlacklistSerializer(serializers.Serializer):
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

            




            

