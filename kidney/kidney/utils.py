from rest_framework.response import Response
from typing import Optional, Dict, Any
from rest_framework.views import exception_handler
from rest_framework_simplejwt.tokens import RefreshToken
from django.template import Template, Context
from django.core.mail import EmailMultiAlternatives
import random
import re
import secrets
import base64
import string
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from rest_framework import status
from asgiref.sync import sync_to_async
from django.db import OperationalError
from django.contrib.auth import get_user_model

def ResponseMessageUtils(
    message:str=None,
    data: Optional[Dict[str, Any]]=None,
    errors: Optional[Dict[str, Any]]=None,
    status_code: int = 200
) -> Response:

    """
        Helper function to return json response

        Args:
            message (str): Message to be included in the response.
            data (dict): Optional Additional data to be returned in the response.
            status_code (int): HTTP status code for the response
            errors (dict): Optional errors to be included in the response

        Returns:
            JsonResponse: Django JsonResponse with the given data.
    """
    response_data = {}

    if message is not None:
        response_data.update({"message": message})

    if errors is not None:
        response_data.update({"errors": errors})

    if data is not None:
        response_data.update({"data": data})

    return Response(response_data, status=status_code)


def allowed_file(filename) -> str:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    """Check if the file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#custom exception handler
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response and isinstance(response.data, dict):
        data = response.data
        # Prioritize non_field_errors if present
        if "non_field_errors" in data and isinstance(data["non_field_errors"], list):
            response.data = {"message": data["non_field_errors"][0]} #flatten the error
        else:
            for key, value in data.items():
                if isinstance(value, list) and len(value) == 1:
                    response.data = {"message": value[0]} #flatten the error
                    break  # stop after first useful messageatten list
            
         
    return response


#generate a refresh token for the given user using RefreshToken
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh_token': str(refresh),
        'access_token': str(refresh.access_token),
    }


def send_otp_to_email(
    subject=None,
    message=None,
    recipient_list=None,
    otp=None,
):
    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        to=recipient_list,
    )

    html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #333;">(OTP) Code</h2>
                <p>Hello, {{ recipient_list }}</p>
                <p>Use the following OTP to verify your email:</p>
                <p style="font-size: 24px; font-weight: bold; color: #4CAF50;">{{ otp }}</p>
                <p>This code will expire in 3 minutes.</p>
                <hr>
                <p style="font-size: 12px; color: #888;">If you did not request this, please ignore this email.</p>
                <p style="font-size: 12px; color: #888;">Thank you,<br>KidneyCare Team</p>
            </div>
        </body>
        </html>
    """)

    context = Context({'otp': otp, 'recipient_list': recipient_list[0]})
    html_content = html_template.render(context)

    email.attach_alternative(html_content, "text/html")

    email.send(fail_silently=False)


def send_password_to_email(
    subject=None,
    message=None,
    recipient_list=None,
    password=None
):
    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        to=recipient_list,
    )

    html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #333;">(Generated) Password</h2>
                <p>Hello, {{ recipient_list }}</p>
                <p>Please use the following temporary password to log in to your account:</p>
                <p style="font-size: 24px; font-weight: bold; color: #4CAF50;">{{ password }}</p>
                <p>For your security, please change this password after logging in and do not share it with anyone.</p>
                <hr>
                <p style="font-size: 12px; color: #888;">If you did not request this, please ignore this email.</p>
                <p style="font-size: 12px; color: #888;">Thank you,<br>KidneyCare Team</p>
            </div>
        </body>
        </html>
    """)

    context = Context({'password': password, 'recipient_list': recipient_list[0]})
    html_content = html_template.render(context)

    email.attach_alternative(html_content, "text/html")

    email.send(fail_silently=False)


#generate a random otp 6-digit number
def generate_otp():
    return f"{random.randint(100000, 999999)}"

#password generator
def generate_password(password_length=8):

    #define the possible characters for the password
    alphabet = string.digits
    # alphabet = string.ascii_letters + string.digits + string.punctuation.replace('/', '').replace('\\', '').replace('"', '')

    #generate a random password by joining randomly chosen characters
    password = ''.join(secrets.choice(alphabet) for _ in range(password_length))

    return password

#a helper function that validate the email
def validate_email(email):
    #check if the email matches the regex pattern for a valid email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        #if the email does not match the pattern, return False
        return False
     #if the email matches the pattern, return True (indicating it's valid)
    return True

#a helper function that validates empty fields
def is_field_empty(field_name):
    if field_name is None:  
        return True
    if isinstance(field_name, str) and field_name.strip() == "":
        return True
    if isinstance(field_name, (list, dict)) and not field_name:
        return True
    return False

#a helper function that extracts the first error message
def extract_first_error_message(errors):
    if isinstance(errors, dict):
        for k, v in errors.items():
            #if value is a list return the first message
            if isinstance(v, list) and v:
                return v[0] #flatten the error message
            #if value is a dict, recurse
            elif isinstance(v, dict):
                message = extract_first_error_message(v)
                if message:
                    return message
            else:
                return v
    elif isinstance(errors, list) and errors:
        return errors[0] #flatten the error
    return None

def get_token_user_id(request):

    #get the 'Authorization' header from the request, or return an empty list if not found
    auth_header = request.headers.get('Authorization', '')

    #check if the 'Authorization' header is missing or doesn't start with Bearer
    if not auth_header or not auth_header.startswith('Bearer '):
        return ResponseMessageUtils(
            message="Missing or invalid Authorization header",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    try:
        # Extract the token part from the Authorization header
        auth_header_token = auth_header.split(' ')[1]
    except IndexError:
        return ResponseMessageUtils(
            message="Malformed Authorization header",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    try:
        #parse the token using AccessToken
        access_token = AccessToken(auth_header_token)

        #extract the user_id claim, convert to string and remove hyphens
        return str(access_token["user_id"])
    except TokenError as e:
        #handle invalid or expired tokens by returning a 401 Unauthorized
        return ResponseMessageUtils(
            message="Expired or invalid token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
            
    
@sync_to_async
def get_user_by_id(user_id):
    try:
        User = get_user_model()
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
    except OperationalError as e:
        print(f"[DB ERROR] OperationalError while fetching user {user_id}: {e}")
        return None
    except Exception as e:
        print(f"[UNEXPECTED ERROR] Failed to fetch user {user_id}: {e}")
        return None
    
def get_base64_file_size(base64_data: str) -> int:
    """
    Returns the size in bytes of the base64-encoded image.
    """
    if ";base64," in base64_data:
        base64_data = base64_data.split(";base64,")[1]
    return len(base64.b64decode(base64_data))