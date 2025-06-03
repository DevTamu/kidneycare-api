from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework import status
from app_authentication.models import User
from kidney.utils import ResponseMessageUtils, get_token_user_id
from django.db.models import Q
from .serializers import (
    GetUsersMessageSerializer,
    GetNotificationChatsToProviderSerializer,
    GetProvidersChatSerializer,
    GetProviderChatInformationSerializer,
    GetPatientsChatSerializer,
    GetPatientChatInformationSerializer
)
from django.shortcuts import get_object_or_404
from .models import Message
import logging
logger = logging.getLogger(__name__)

class GetUsersMessageView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetUsersMessageSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Message.objects.all()
    
    def get_object(self):
        
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        #get the current user
        user = self.request.user

        #filter the queryset to include only messages between the logged-in user and the user with the given ID
        queryset = self.filter_queryset(self.get_queryset().filter(
            Q(sender=user, receiver__id=id) |
            Q(sender__id=id, receiver=user)
        ))

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        obj = get_object_or_404(queryset, **filter_kwargs)

        #may raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

class GetNotificationChatsToProviderView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetNotificationChatsToProviderSerializer
       
    
    def get_queryset(self):
        return Message.objects.all()


    def get(self, request, *args, **kwargs):

        try:
            messages = self.get_queryset().filter(receiver=request.user)

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
                sender_messages__receiver=patient
            ).distinct()

            if not providers_who_messaged_patient.exists():
                return ResponseMessageUtils(
                    message="No messages found",
                    data=[],
                    status_code=status.HTTP_404_NOT_FOUND
                )

            latest_messages = []
            for provider in providers_who_messaged_patient:
                message = Message.objects.filter(
                    sender=provider,
                    receiver=patient
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
                message=f"Something went wrong while processing your request. {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetProviderChatInformationView(generics.RetrieveAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = GetProviderChatInformationSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return User.objects.get(id=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):

        try:

            queryset = self.get_queryset()

            serializer = self.get_serializer(queryset)

            return ResponseMessageUtils(
                message="Provider Chat",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message=f"Something went wrong while processing your request. {e}",
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
                sender_messages__receiver=admin
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
                    sender=patient,
                    receiver=admin
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
                message=f"Something went wrong while processing your request. {e}",
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

            queryset = self.get_queryset()

            serializer = self.get_serializer(queryset)

            return ResponseMessageUtils(
                message="User Chat",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message=f"Something went wrong while processing your request. {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )