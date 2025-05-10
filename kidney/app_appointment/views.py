from .serializers import (
    CreateAppointmentSerializer,
    GetAppointmentsInProviderSerializer,
    GetAppointmentDetailsInProviderSerializer,
    GetAppointmentsInAdminSerializer,
    UpdateAppointmentInPatientSerializer,
    AddAppointmentDetailsInAdminSerializer
)
from .models import Appointment
from rest_framework import generics, status
from kidney.utils import ResponseMessageUtils, extract_first_error_message
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
import logging
import uuid
from .models import AssignedAppointment


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
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return ResponseMessageUtils(message=f"Something went wrong: {e}", status_code=status.HTTP_400_BAD_REQUEST)


class UpdateAppointmentInPatientView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateAppointmentInPatientSerializer
    lookup_field = 'pk'

    def put(self, request, *args, **kwargs):

        try:
            queryset = Appointment.objects.get(id=self.kwargs.get('pk'))
            serializer = self.get_serializer(instance=queryset, data=request.data)

            if serializer.is_valid():
                serializer.save()

                return ResponseMessageUtils(
                    message="Your Appointment has been successfully updated",
                    status_code=status.HTTP_200_OK
                )
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"qweqweq: {str(e)}")
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class AddAppointmentDetailsInAdminView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = AddAppointmentDetailsInAdminSerializer
    queryset = AssignedAppointment.objects.all()
    lookup_field = 'pk' #captures pk from the url

    def perform_create(self, serializer):
        appointment = Appointment.objects.get(id=self.kwargs.get('pk'))
        return serializer.save(appointment=appointment)
    


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