from .serializers import (
    CreateAppointmentSerializer,
    GetAppointmentsInProviderSerializer,
    GetPatientInformationSerializer,
    # GetAppointmentsInAdminSerializer,
    UpdateAppointmentInPatientSerializer,
    AddAppointmentDetailsInAdminSerializer,
    GetPatientAppointmentHistorySerializer,
    GetPendingAppointsmentsInAdminSerializer,
    CancelAppointmentSerializer
)
from app_authentication.models import User
from .models import Appointment
from rest_framework import generics, status
from kidney.utils import ResponseMessageUtils, extract_first_error_message
from rest_framework.permissions import IsAuthenticated
import logging
from .models import AssignedAppointment
from rest_framework.pagination import PageNumberPagination

logger = logging.getLogger(__name__)

class AppointmentPagination(PageNumberPagination):
    page_size = 10  #define how many appointments to show per page
    page_size_query_param = 'page'  # Allow custom page size via query params
    max_page_size = 25  # Maximum allowed page size

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
    lookup_field = 'pk' #capture the pk to the url

    def put(self, request, *args, **kwargs):

        try:
            #get the patient appointment by id
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
    pagination_class = AppointmentPagination

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

            paginator = self.pagination_class()
            paginated_appointments = paginator.paginate_queryset(appointments, request)
            serializer = self.get_serializer(paginated_appointments, many=True)

            paginated_response = paginator.get_paginated_response(serializer.data)

            return ResponseMessageUtils(message="List of Appointments", data=paginated_response.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error: {e}")
            return ResponseMessageUtils(message=f"Something went wrong: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)
        

class GetPatientInformationView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientInformationSerializer
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        
        try:
            user = User.objects.get(id=kwargs.get('pk'))
            serializer = self.get_serializer(user, data=request.data)
            if serializer.is_valid():
                return ResponseMessageUtils(message="User information", data=serializer.data, status_code=status.HTTP_200_OK)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"qweqwe: {str(e)}")
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
   
    
class GetPatientAppointmentHistoryView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientAppointmentHistorySerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Appointment.objects.filter(user_id=self.kwargs.get('pk'), status='Completed')

    def get(self, request, *args, **kwargs):

        try:
            serializer = self.get_serializer(self.get_queryset(), many=True)
            return ResponseMessageUtils(message="List of Appointment history", data=serializer.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
      

class GetPendingAppointsmentsInAdminView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPendingAppointsmentsInAdminSerializer
    queryset = Appointment.objects.filter(status='Pending')


class CancelAppointmentView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CancelAppointmentSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Appointment.objects.filter(id=self.kwargs.get('pk'))
    
    def delete(self, request, *args, **kwargs):
        
        try:
            instance = self.get_queryset()
            instance.delete()
            return ResponseMessageUtils(message="Successfully Deleted", status_code=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return ResponseMessageUtils(message="Appointment not found", status_code=status.HTTP_400_BAD_REQUEST)    
        except Exception as e:
            return ResponseMessageUtils(message="Something went wrong", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)    


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