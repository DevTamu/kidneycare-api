from django.shortcuts import render
from .serializers import (
    CreateAppointmentSerializer,
    GetAppointmentsInProviderSerializer,
    GetAppointmentDetailsInProviderSerializer,
    GetAppointmentsInAdminSerializer
)
from .models import Appointment
from rest_framework import generics, status
from kidney.utils import ResponseMessageUtils
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
import logging
import uuid

logger = logging.getLogger(__name__)

class CreateAppointmentView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = CreateAppointmentSerializer


    def post(self, request, *args, **kwargs):

        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(message="Successfully created appointment", status_code=status.HTTP_201_CREATED)
            logger.error(f"Error: {serializer.errors}")
            return ResponseMessageUtils(message=serializer.errors["message"][0], status_code=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return ResponseMessageUtils(message=f"Something went wrong: {e}", status_code=status.HTTP_400_BAD_REQUEST)


class GetAppointmentInProviderView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = GetAppointmentsInProviderSerializer

    def get(self, request, *args, **kwargs):

        try:
            appointment = Appointment.objects.all()
            serializer = self.get_serializer(appointment, many=True)
            return ResponseMessageUtils(message="List of Appointments", data=serializer.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error: {e}")
            return ResponseMessageUtils(message=f"Something went wrong: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)
        

class GetAppointmentDetailsInProviderView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetAppointmentDetailsInProviderSerializer
    lookup_field = 'id'
    def get_queryset(self):
        return Appointment.objects.all()
    
    def get_object(self):   
        
        raw_id = self.kwargs.get('id')

        try:
            #convert 32-char hex string into UUID object
            user_id = uuid.UUID(hex=raw_id)

        except (ValueError):
            raise NotFound("Invalid user ID format")
        
        return self.get_queryset().get(user__id=user_id)
    
        

class GetAppointmentInAdminView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = GetAppointmentsInAdminSerializer

    def get(self, request, *args, **kwargs):

        try:
            appointment = Appointment.objects.all()
            serializer = self.get_serializer(appointment, many=True)
            return ResponseMessageUtils(message="List of Appointments", data=serializer.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error: {e}")
            return ResponseMessageUtils(message=f"Something went wrong: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)