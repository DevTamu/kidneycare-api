from rest_framework.response import Response
from typing import Optional, Dict, Any
from rest_framework.views import exception_handler
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMessage
from django.conf import settings
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
    # return filename.endswith(('jpg', 'jpeg', 'png'))


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response and isinstance(response.data, dict):
        for key, value in response.data.items():
            if isinstance(value, list) and len(value) == 1:
                response.data[key] = value[0]  # flatten list
            elif 'non_field_errors' in response.data:
                response.data = {
                    "message": value[0]
                }


    return response

#creating tokens manually when user register an account
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def send_email_utils(
    subject=None,
    message=None,
    from_email=None,
    recipient_list=None,
):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=recipient_list,
    )
    email.send(fail_silently=False)