from .serializers import (
    CreateAppointmentSerializer,
    GetAppointmentsInProviderSerializer,
    GetAppointmentDetailsInProviderSerializer,
    # GetAppointmentsInAdminSerializer,
    UpdateAppointmentInPatientSerializer,
    AddAppointmentDetailsInAdminSerializer
)
from app_authentication.models import User
from .models import Appointment
from rest_framework import generics, status
from kidney.utils import ResponseMessageUtils, extract_first_error_message
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
import logging
import uuid
from .models import AssignedAppointment
from django.shortcuts import get_object_or_404

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
            
            #get all AssignedAppointment entries where current user is a provider
            assigned_appointments = AssignedAppointment.objects.filter(
                assigned_providers__assigned_provider=request.user,
                appointment__status__in=['Approved', 'In-Progress']
            ).distinct()
            
            #get the related appointment IDS
            appointment_ids = assigned_appointments.values_list('appointment_id', flat=True)

            #fetch the appointments
            appointments = Appointment.objects.filter(id__in=appointment_ids).distinct()

            serializer = self.get_serializer(appointments, many=True)
            filtered_data = [item for item in serializer.data if item]
            return ResponseMessageUtils(message="List of Appointments", data=filtered_data, status_code=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error: {e}")
            return ResponseMessageUtils(message=f"Something went wrong: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)
        

class GetAppointmentDetailsInProviderView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetAppointmentDetailsInProviderSerializer
    queryset = Appointment.objects.all()
    lookup_field = 'pk'

    def get_queryset(self):   
        return Appointment.objects.get(user__id=self.kwargs.get('pk'))
    
    # def get_object(self):

    #     # Perform the lookup filtering.
    #     lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

    #     queryset = self.filter_queryset(self.get_queryset().filter(user__id=self.kwargs.get('pk')))

    #     filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

    #     obj = get_object_or_404(queryset, **filter_kwargs)

    #     #may raise a permission denied
    #     self.check_object_permissions(self.request, obj)

    #     return obj
    
   
    
        

# class GetAppointmentInAdminView(generics.ListAPIView):

#     permission_classes = [IsAuthenticated]

#     serializer_class = GetAppointmentsInAdminSerializer

#     def get(self, request, *args, **kwargs):

#         try:
#             appointment = Appointment.objects.all()
#             serializer = self.get_serializer(appointment, many=True)
#             return ResponseMessageUtils(message="List of Appointments", data=serializer.data, status_code=status.HTTP_200_OK)
#         except Exception as e:
#             logger.error(f"Error: {e}")
#             return ResponseMessageUtils(message=f"Something went wrong: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)