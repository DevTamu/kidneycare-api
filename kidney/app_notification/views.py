from rest_framework import generics, status
from kidney.utils import ResponseMessageUtils, extract_first_error_message, get_token_user_id
from .serializers import NotificationsInPatientSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Notification

class NotificationsInPatientView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationsInPatientSerializer

    def get_queryset(self):
        return Notification.objects.select_related('appointment').all()

    def get(self, request, *args, **kwargs):

        try:

            #get the user id from the token
            user_id = get_token_user_id(request)

            notification = self.get_queryset().filter(appointment__user=user_id)

            if not notification:
                return ResponseMessageUtils(message="No notifications found", status_code=status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(notification, many=True)

            return ResponseMessageUtils(message="List of notifications", data=serializer.data, status_code=status.HTTP_200_OK)

        except Exception as e:
            print(f"ERROR: {e}")
            return ResponseMessageUtils(
                message=f"Something went wrong while processing your request {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )