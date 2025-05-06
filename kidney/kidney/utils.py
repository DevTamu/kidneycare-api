from rest_framework.response import Response
from typing import Optional, Dict, Any
from rest_framework.views import exception_handler
from rest_framework_simplejwt.tokens import RefreshToken
from django.template import Template, Context
from django.core.mail import EmailMultiAlternatives
import random
import re
import secrets
import string

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
            data (dict): Additional data to be returned in the response.
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


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response and isinstance(response.data, dict):
        
        for key, value in response.data.items():
            if isinstance(value, list) and len(value) == 1:
                response[key] = {
                    "message": value[0]
                }
    return response


#generate a refresh token for the given user using RefreshToken
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
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


#generate a random 6-digit number between 100000 and 999999
def generate_otp():
    return f"{random.randint(100000, 999999)}"

#password generator that generate random password
def generate_password(password_length=24):

    #define the possible characters for the password
    alphabet = string.ascii_letters + string.digits + string.punctuation.replace('/', '').replace('\\', '')

    #generate a random password  
    password = ''.join(secrets.choice(alphabet) for _ in range(password_length))

    return password


def validate_email(email):
    #check if the email matches the regex pattern for a valid email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        #if the email does not match the pattern, return False
        return False
     #if the email matches the pattern, return True (indicating it's valid)
    return True

def is_field_empty(field_name):
    if field_name is None:
        return True
    if isinstance(field_name, str) and field_name.strip() == "":
        return True
    if isinstance(field_name, (list, dict)) and not field_name:
        return True
    return False
    