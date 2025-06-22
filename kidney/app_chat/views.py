from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework import status
from app_authentication.models import User
from kidney.utils import ResponseMessageUtils, get_token_user_id, extract_first_error_message
from django.db.models import Q
from .serializers import (
    GetNotificationChatsToProviderSerializer,
    GetProvidersChatSerializer,
    GetProviderChatInformationSerializer,
    GetPatientsChatSerializer,
    UpdateChatStatusInAdminSerializer,
    GetPatientChatInformationSerializer,
    UpdateNotificationChatInProviderSerializer,
)
from rest_framework.exceptions import ParseError, NotFound
import json
from .models import Message
from rest_framework.pagination import PageNumberPagination

class ChatPagination(PageNumberPagination):
    page_size = 10  #define how many appointments to show per page
    page_size_query_param = 'limit'  # Allow custom page size via query params
    max_page_size = 10  # Maximum allowed page size
    page_query_param = 'page'

class GetNotificationChatsToProviderView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetNotificationChatsToProviderSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        return Message.objects.filter(receiver=self.request.user)

    def get(self, request, *args, **kwargs):

        try:
            messages = self.get_queryset()

            serializer = self.get_serializer(messages, many=True)

            return ResponseMessageUtils(
                message="List of notification messages",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class UpdateNotificationChatInProviderView(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class     = UpdateNotificationChatInProviderSerializer
    lookup_field = 'pk'
    queryset = Message.objects.all()

    def patch(self, request, *args, **kwargs):

        try:

            instance = self.get_object()

            serializer = self.get_serializer(instance=instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(
                    message="Successfully update the notification status",
                    status_code=status.HTTP_200_OK
                )
            
            return ResponseMessageUtils(
                message=extract_first_error_message(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return ResponseMessageUtils(
                message=f"Something went wrong while processing your request. {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetProvidersChatView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetProvidersChatSerializer

    def get(self, request, *args, **kwargs):
        
        try:
            #get the current authenticated user_id from the token
            user_id = get_token_user_id(request)

            patient = User.objects.get(id=user_id)

            providers = User.objects.filter(role__in=['nurse', 'head nurse'])

            providers_who_messaged_patient = providers.filter(
                Q(sender_messages__receiver=patient) | Q(receiver_messages__sender=patient)
            ).distinct()

            if not providers_who_messaged_patient.exists():
                return ResponseMessageUtils(
                    message="No messages found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            latest_messages = []
            for provider in providers_who_messaged_patient:
                message = Message.objects.filter(
                    Q(sender=patient, receiver=provider) |
                    Q(sender=provider, receiver=patient)
                ).order_by('-created_at').first()
                if message:
                    latest_messages.append(message)
       

            serializer = self.get_serializer(latest_messages, many=True, context={'pk': user_id, 'request': request})


            return ResponseMessageUtils(
                message="List of chat users",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetProviderChatInformationView(generics.ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = GetProviderChatInformationSerializer
    lookup_field = 'pk'

        

    def get(self, request, *args, **kwargs):

        try:

            user_id = get_token_user_id(request)

            queryset = User.objects.get(id=kwargs.get('pk'))

            serializer = self.get_serializer(queryset, context={'user_id': user_id, 'request': request})
            return ResponseMessageUtils(
                message="Chat messages",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message=f"Something went wrong while processing your request {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    
class GetPatientsChatView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientsChatSerializer

    def get(self, request, *args, **kwargs):
        
        try:
            #get the current authenticated user_id from the token
            user_id = get_token_user_id(request)

            admin = User.objects.get(id=user_id)

            patient = User.objects.filter(role='patient')

            patient_who_messaged_admin = patient.filter(
                Q(sender_messages__receiver=admin) | Q(receiver_messages__sender=admin)
            ).distinct()

            if not patient_who_messaged_admin.exists():
                return ResponseMessageUtils(
                    message="No messages found",
                    data=[],
                    status_code=status.HTTP_404_NOT_FOUND
                )

            latest_messages = []
            for patient in patient_who_messaged_admin:
                message = Message.objects.filter(
                    Q(sender=patient, receiver=admin) |
                    Q(sender=admin, receiver=patient)
                ).order_by('-created_at').first()
                if message:
                    latest_messages.append(message)
       

            serializer = self.get_serializer(latest_messages, many=True, context={'pk': user_id, 'request': request})


            return ResponseMessageUtils(
                message="List of chats",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class UpdateChatStatusInView(generics.UpdateAPIView): 

    serializer_class = UpdateChatStatusInAdminSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return User.objects.get(id=self.kwargs.get('pk'))
            
    def patch(self, request, *args, **kwargs):

        try:
            
            sender_id = get_token_user_id(request)
            receiver_id = kwargs.get('pk')

            instance = self.get_queryset()

            serializer = self.get_serializer(instance=instance, data=request.data, context={"sender_id": sender_id, "receiver_id": receiver_id}, partial=True)
            
            if serializer.is_valid():
                serializer.save()

                return ResponseMessageUtils(
                    message="Successfully updated",
                    status_code=status.HTTP_200_OK
                )
            
            return ResponseMessageUtils(
                message=extract_first_error_message(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            print(f"WHAT WENT WRORNG? {e}")
            return ResponseMessageUtils(
                message="Something went wrong while processing your request",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        
class GetPatientChatInformationView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientChatInformationSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return User.objects.get(id=self.kwargs.get('pk'))
        
    def get(self, request, *args, **kwargs):

        try:

            user_id = get_token_user_id(request)

            queryset = self.get_queryset()

            serializer = self.get_serializer(queryset, context={"user_id": user_id, "request": request})

            return ResponseMessageUtils(
                message="Chat messages",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        



