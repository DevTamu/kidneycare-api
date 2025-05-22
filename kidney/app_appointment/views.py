from .serializers import (
    CreateAppointmentSerializer,
    GetAppointmentsInProviderSerializer,
    GetPatientInformationSerializer,
    UpdateAppointmentInPatientSerializer,
    AddAppointmentDetailsInAdminSerializer,
    GetPatientAppointmentHistorySerializer,
    GetPendingAppointsmentsInAdminSerializer,
    CancelAppointmentSerializer,
    GetPatientUpcomingAppointmentsSerializer,
    GetPatientUpcomingAppointmentSerializer,
    # GetAllPatientUpcomingAppointmentInAppointmentPageSerializer,
    CancelPatientUpcomingAppointmentInAppointmentPageSerializer,
    # ReschedulePatientAppointmentSerializer
)
from app_authentication.models import User
from .models import Appointment
from rest_framework import generics, status
from kidney.utils import (
    ResponseMessageUtils,
    extract_first_error_message,
    get_token_user_id
)
from rest_framework.permissions import IsAuthenticated
import logging
from .models import AssignedAppointment
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta

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
                return ResponseMessageUtils(message="Successfully created an appointment", status_code=status.HTTP_201_CREATED)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateAppointmentInPatientView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateAppointmentInPatientSerializer
    lookup_field = 'pk' #capture the pk to the url

    def patch(self, request, *args, **kwargs):

        try:
            
            appointment = Appointment.objects.filter(id=self.kwargs.get('pk')).first()

            if not appointment:
                return ResponseMessageUtils(message="No appointment found", status_code=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(instance=appointment, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(
                    message="Your Appointment has been successfully updated",
                    status_code=status.HTTP_200_OK
                )
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f'qwewqewq: {e}')
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class AddAppointmentDetailsInAdminView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = AddAppointmentDetailsInAdminSerializer
    # queryset = AssignedAppointment.objects.all()
    lookup_field = 'pk' #captures pk from the url


    def post(self, request, *args, **kwargs):

        try:
            appointment = Appointment.objects.get(id=self.kwargs.get('pk'))

            serializer = self.get_serializer(data=request.data, context={'appointment_pk': appointment})

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(message="Successfully added Appointment details", status_code=status.HTTP_201_CREATED)
            print(f'qwewqeq: {str(serializer.errors)}')
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # def perform_create(self, serializer):
    #     appointment = Appointment.objects.get(id=self.kwargs.get('pk'))
    #     result = serializer.save(appointment=appointment)
    #     print(f'RESULT: {result}')
    #     return result
    


class GetAppointmentInProviderView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetAppointmentsInProviderSerializer
    pagination_class = AppointmentPagination

    def get(self, request, *args, **kwargs):  
        try:
            
            #get all AssignedAppointment entries where current user is a provider
            assigned_appointments = AssignedAppointment.objects.filter(
                assigned_provider__assigned_provider=request.user,
                appointment__status__in=['Approved', 'In-Progress']
            )
            
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
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

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
        return Appointment.objects.get(id=self.kwargs.get('pk'))
    
    def delete(self, request, *args, **kwargs):
        
        try:
            instance = self.get_queryset()
            instance.delete()
            return ResponseMessageUtils(message="Successfully Deleted", status_code=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return ResponseMessageUtils(message="Appointment not found", status_code=status.HTTP_400_BAD_REQUEST)    
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetPatientUpcomingAppointmentView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientUpcomingAppointmentSerializer

    def get(self, request, *args, **kwargs):
        
        #user id of the current authenticated user
        user_id = get_token_user_id(request)
        
        try:

            # today = datetime.today().date()
            # #starting 1 day before the upcoming appointment
            # start = datetime.combine(today + timedelta(days=1), datetime.min.time())
            # #ending 1 day before the upcoming appointment
            # end = datetime.combine(today + timedelta(days=1), datetime.max.time())
            
            #get the most recently created appointment for the patient/user
            user_appointment = Appointment.objects.filter(
                user_id=user_id,
                # date__range=(start, end),
            ).order_by('-created_at').first()

            if not user_appointment:
                return ResponseMessageUtils(message="No upcoming apppointment found", status_code=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(user_appointment)
            return ResponseMessageUtils(message="Upcoming appointment", data=serializer.data, status_code=status.HTTP_200_OK)    
        except Exception as e:
            print(f'qwewqe: {e}')
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetPatientUpcomingAppointmentsInHomeView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientUpcomingAppointmentsSerializer

    def get(self, request, *args, **kwargs):
        
        #get the user id of the current authenticated user
        user_id = get_token_user_id(request)
        
        try:
            
            #get all the appointments associated to the current authenticated user
            user_appointment = Appointment.objects.filter(user_id=user_id).order_by('date')
            
            if not user_appointment:
                return ResponseMessageUtils(message="No upcoming apppointment found", status_code=status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(user_appointment, many=True)
            return ResponseMessageUtils(message="List of Upcoming appointment", data=serializer.data, status_code=status.HTTP_200_OK)    
        except Exception as e:
            print(f'MARTIN: {str(e)}')
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# class GetAllPatientUpcomingAppointmentInAppointmentView(generics.ListAPIView):

#     permission_classes = [IsAuthenticated]
#     serializer_class = GetAllPatientUpcomingAppointmentInAppointmentPageSerializer

#     def get(self, request, *args, **kwargs):
        
#         #get the token user id of the current authenticated user
#         user_id = get_token_user_id(request)
        
#         try:
            
#             #get all the appointments associated to the current authenticated user
#             user_appointment = Appointment.objects.filter(
#                 user_id=user_id,
#                 status='Approved'
#             ).order_by('date')


#             serializer = self.get_serializer(user_appointment, many=True)
#             return ResponseMessageUtils(message="List of Upcoming appointment", data=serializer.data, status_code=status.HTTP_200_OK)    
#         except Exception as e:
#             print(f'qwewqe: {str(e)}')
#             return ResponseMessageUtils(
#                 message="Something went wrong while processing your request.",
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            # )


class CancelPatientUpcomingAppointmentInAppointmentView(generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = CancelPatientUpcomingAppointmentInAppointmentPageSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Appointment.objects.get(id=self.kwargs.get('pk'))
    
    def delete(self, request, *args, **kwargs):
        
        try:
            instance = self.get_queryset()
            instance.delete()
            return ResponseMessageUtils(message="Successfully Deleted", status_code=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return ResponseMessageUtils(message="Appointment not found", status_code=status.HTTP_400_BAD_REQUEST)    
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


# class ReschedulePatientAppointmentView(generics.UpdateAPIView):

#     permission_classes = [IsAuthenticated]
#     serializer_class = ReschedulePatientAppointmentSerializer
#     lookup_field = 'pk'


#     def patch(self, request, *args, **kwargs):

#         try:

#             appointment = Appointment.objects.filter(id=kwargs.get('pk')).first()

#             if not appointment:
#                 return ResponseMessageUtils(message="No appointment id found", status_code=status.HTTP_404_NOT_FOUND)

#             serializer = self.get_serializer(instance=appointment, data=request.data, partial=True)

#             if serializer.is_valid():
#                 return ResponseMessageUtils(message="Successfully updated your appointment", status_code=status.HTTP_200_OK)
#             return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return ResponseMessageUtils(
#                 message="Something went wrong while processing your request.",
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )