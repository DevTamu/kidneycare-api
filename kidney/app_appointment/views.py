from .serializers import (
    CreateAppointmentSerializer,
    GetAppointmentsInProviderSerializer,
    GetPatientInformationSerializer,
    UpdateAppointmentInPatientSerializer,
    AddAppointmentDetailsInAdminSerializer,
    GetPatientAppointmentHistorySerializer,
    GetAllAppointsmentsInAdminSerializer,
    CancelAppointmentSerializer,
    GetPatientUpcomingAppointmentsSerializer,
    GetPatientUpcomingAppointmentSerializer,
    CancelPatientUpcomingAppointmentInAppointmentPageSerializer,
    GetPatientAppointmentDetailsInAdminSerializer,
    GetUpcomingAppointmentDetailsInPatientSerializer,
)
from app_authentication.models import User
from .models import Appointment, AssignedProvider
from rest_framework import generics, status
from kidney.utils import (
    ResponseMessageUtils,
    extract_first_error_message,
    get_token_user_id
)
from django.db.models import Q
from datetime import timedelta, datetime
from rest_framework.permissions import IsAuthenticated
from .models import AssignedAppointment
from rest_framework.pagination import PageNumberPagination

class AppointmentPagination(PageNumberPagination):
    page_size = 20  #define how many appointments to show per page
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
            print(f"WHAT WENT WRONG?: {e}")
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
            print(f"ERROR MESSAGE: {serializer.errors}")
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"ERROR MESSAGE: {e}")
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    


class GetAppointmentInProviderView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetAppointmentsInProviderSerializer
    pagination_class = AppointmentPagination

    def get(self, request, *args, **kwargs):  
        try:
            
            assigned_appointments = AssignedAppointment.objects.filter(
                # appointment__user=request.user,
                assigned_provider__assigned_provider=request.user,
                appointment__status__in=['Approved', 'In-Progress']
                # assigned_patient_appointment__status__in=['Approved', 'In-Progress']
            )
            #create an instance of the paginator
            paginator = self.pagination_class()
            #assign the assigned appointments in paginate queryset
            paginated_data = paginator.paginate_queryset(assigned_appointments, request)
            serializer = self.get_serializer(paginated_data, many=True)
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
   
    
class GetPatientAppointmentHistoryView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientAppointmentHistorySerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Appointment.objects.select_related('user').filter(
            user_id=self.kwargs.get('pk'),
            status='Completed' or 'completed'
        )

    def get(self, request, *args, **kwargs):

        try:
            serializer = self.get_serializer(self.get_queryset(), many=True)
            return ResponseMessageUtils(message="List of Appointment history", data=serializer.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
      

class GetAllAppointsmentsInAdminView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetAllAppointsmentsInAdminSerializer
    pagination_class = AppointmentPagination
    lookup_field = 'status'

    def get(self, request, *args, **kwargs):
        appointment_status = kwargs.get('status')
        try:

            #if no status path parameter is provided, display all appointments
            if appointment_status in (None, ""):
                appointment = Appointment.objects.all()
            else:
                #filter appointments based on the status path parameter value
                appointment = Appointment.objects.filter(status=appointment_status)

            paginator = self.pagination_class()
            paginated_data = paginator.paginate_queryset(appointment, request)
            serializer = self.get_serializer(paginated_data, many=True)
            paginated_response = paginator.get_paginated_response(serializer.data)
            
            return ResponseMessageUtils(
                message="List of Pending Appointments",
                data=paginated_response.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            print(f"qwewqe: {str(e)}")
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
            next_day = datetime.now() + timedelta(days=1)
                        
            user_appointment = Appointment.objects.filter(
                user_id=user_id,
                date__lte=next_day
            ).first()
   
            if not user_appointment:
                return ResponseMessageUtils(message="No upcoming apppointment found", status_code=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(user_appointment)
            return ResponseMessageUtils(message="Upcoming appointment", data=serializer.data, status_code=status.HTTP_200_OK)    
        except Exception as e:
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
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
        
class GetPatientAppointmentDetailsInAdminView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientAppointmentDetailsInAdminSerializer
    lookup_field = 'pk'
    
    def get(self, request, *args, **kwargs):
        

        try:

            assigned_appointment = Appointment.objects.filter(id=kwargs.get('pk')).first()

            if not assigned_appointment:
                return ResponseMessageUtils(message="No appointment details found", status_code=status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(assigned_appointment)

            return ResponseMessageUtils(message="Appointment details found", data=serializer.data, status_code=status.HTTP_200_OK)

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetUpcomingAppointmentDetailsInPatientView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetUpcomingAppointmentDetailsInPatientSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Appointment.objects.filter(id=self.kwargs.get('pk'), status='Approved').first()
    
    def get(self, request, *args, **kwargs):

        try:

            appointment = self.get_queryset()

            if not appointment:
                return ResponseMessageUtils(message="No appointment details found", status_code=status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(appointment, many=False)

            return ResponseMessageUtils(message="Appointment details found", data=serializer.data)

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

