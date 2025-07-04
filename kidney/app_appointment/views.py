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
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import F, DateTimeField, ExpressionWrapper, Q
from django.utils import timezone
from app_authentication.models import User
from .models import Appointment
from rest_framework import generics, status
from kidney.utils import (
    ResponseMessageUtils,
    extract_first_error_message,
    get_token_user_id
)
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from .models import AssignedAppointment
from kidney.pagination.appointment_pagination import Pagination

class CreateAppointmentView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = CreateAppointmentSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                
                created_appointment = serializer.save()
                
                appointment = Appointment.objects.get(id=created_appointment.id)
                user = appointment.user

                #create an instance of channel layer
                channel_layer = get_channel_layer()

                #get the machine that linked to the created appointment
                assigned_machine_obj = created_appointment.assigned_machine_appointment.first()

                assigned_machine = assigned_machine_obj.assigned_machine if assigned_machine_obj else None

                assigned_provider_obj = appointment.assigned_patient_appointment.first()

                assigned_provider = assigned_provider_obj.assigned_provider if assigned_provider_obj else None

                get_provider_profile = (
                    request.build_absolute_uri(getattr(getattr(assigned_provider, 'user_profile', None), 'picture', None).url)
                    if getattr(getattr(assigned_provider, 'user_profile', None), 'picture', None)
                    else None
                )

                async_to_sync(channel_layer.group_send)(
                    f"appointment_user_{user.id}",
                    {
                        "type": "upcoming_appointments",
                        "date": appointment.date.strftime("%m/%d/%Y"),
                        "time": appointment.time.strftime("%I:%M %p"),
                        "patient_id": str(user.id),
                        "appointment_id": appointment.id,
                        "nurse_id": str(assigned_provider.id) if assigned_provider else None,
                        "status": str(appointment.status).lower(),
                        "machine": f"machine #{assigned_machine}",
                        "provider_name": str(assigned_provider.first_name).lower() if assigned_provider else None,
                        "provider_image": get_provider_profile
                    }
                ) 
            

                return ResponseMessageUtils(message="Successfully created an appointment", status_code=status.HTTP_201_CREATED)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return ResponseMessageUtils(
                message=f"Something went wrong while processing your request {e}",
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
    lookup_field = 'pk' #captures pk from the url


    def post(self, request, *args, **kwargs):

        try:

            appointment = Appointment.objects.get(id=self.kwargs.get('pk'))

            serializer = self.get_serializer(data=request.data, many=False, context={'appointment_pk': appointment})

            if serializer.is_valid():
                
                updated_appointment = serializer.save()
                #get the user linked to the updated appointment
                user = updated_appointment.appointment.user
                #create an instance of channel layer
                channel_layer = get_channel_layer()

                assigned_machine_obj = appointment.assigned_machine_appointment.first()

                assigned_machine = assigned_machine_obj.assigned_machine if assigned_machine_obj else None

                assigned_provider_obj = appointment.assigned_patient_appointment.first()

                assigned_provider = assigned_provider_obj.assigned_provider if assigned_provider_obj else None

                get_provider_profile = (
                    request.build_absolute_uri(getattr(getattr(assigned_provider, 'user_profile', None), 'picture', None).url)
                    if getattr(getattr(assigned_provider, 'user_profile', None), 'picture', None)
                    else None
                )

                if updated_appointment.appointment.status == "approved":
                    async_to_sync(channel_layer.group_send)(
                        f"appointment_user_{user.id}",
                        {
                            "type": "upcoming_appointments",
                            "date": updated_appointment.appointment.date.strftime("%m/%d/%Y"),
                            "time": updated_appointment.appointment.time.strftime("%I:%M %p"),
                            "patient_id": str(user.id),
                            "appointment_id": updated_appointment.appointment.id,
                            "nurse_id": str(assigned_provider.id) if assigned_provider else None,
                            "status": str(updated_appointment.appointment.status).lower(),
                            "machine": f"machine #{assigned_machine}",
                            "provider_name": str(assigned_provider.first_name).lower(),
                            "provider_image": get_provider_profile
                        }
                    )   

                return ResponseMessageUtils(message="Successfully added Appointment details", status_code=status.HTTP_201_CREATED)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"WHAT WENT WRONG? {e}")
            return ResponseMessageUtils(
                message=f"Something went wrong while processing your request. {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetAppointmentInProviderView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetAppointmentsInProviderSerializer
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):  
        try:
            
            user = User.objects.filter(
                id=request.user.id,
                role__in=['nurse', 'head nurse']
            ).first()

            assigned_appointments_to_provider = Appointment.objects.select_related('user').filter(
                Q(assigned_patient_appointment__assigned_provider=user) |
                Q(assigned_patient_appointment__assigned_provider__isnull=True),
                status__in=['pending', 'approved', 'check-in', 'in-progress', 'no show', 'rescheduled']
            )

            #create an instance of the paginator
            paginator = self.pagination_class()
            #assign the assigned appointments in paginate queryset
            paginated_data = paginator.paginate_queryset(assigned_appointments_to_provider, request)
            serializer = self.get_serializer(paginated_data, many=True)
            paginated_response = paginator.get_paginated_response(serializer.data)
            
            return ResponseMessageUtils(message="List of Appointments", data=paginated_response.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            print(f"WHAT WENT WRONG?")
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
            status='completed'
        )

    def get(self, request, *args, **kwargs):

        try:

            if not self.get_queryset():
                return ResponseMessageUtils(message="No appointment history found", status_code=status.HTTP_404_NOT_FOUND)

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
    pagination_class = Pagination
    # lookup_field = 'status'

    def get(self, request, *args, **kwargs):
        # appointment_status = kwargs.get('status')
        try:

            #if no status path parameter is provided, display all appointments
            # if appointment_status in (None, ""):
            #     appointment = Appointment.objects.all()
            # else:
                #filter appointments based on the status path parameter value
            appointment = Appointment.objects.filter(status='pending')

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
            print(f"WHAT WENT WRONG? {e}")
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CancelAppointmentView(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = CancelAppointmentSerializer
    lookup_field = 'pk'
    queryset = Appointment.objects.all()


    def patch(self, request, *args, **kwargs):
        
        try:
            
            appointment = self.get_object()
              
            serializer = self.get_serializer(instance=appointment, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(
                    message="You have been successfully cancelled your appointment",
                    status_code=status.HTTP_200_OK
                )
            
            return ResponseMessageUtils(
                message=extract_first_error_message(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Appointment.DoesNotExist:
            return ResponseMessageUtils(
                message="Appointment not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
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
            now = timezone.now()
                        
            appointments = Appointment.objects.annotate(
                valid_time=ExpressionWrapper(F('date') + timedelta(hours=24), output_field=DateTimeField())
            ).filter(
                user_id=user_id,
                valid_time__gte=now,   
                status='approved'
            ).order_by('date', 'id').first()
   
            if not appointments:
                return ResponseMessageUtils(message="No upcoming apppointment found", status_code=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(appointments)
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

class CancelPatientUpcomingAppointmentInAppointmentView(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = CancelPatientUpcomingAppointmentInAppointmentPageSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Appointment.objects.get(id=self.kwargs.get('pk'))
    
    def patch(self, request, *args, **kwargs):
        
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
        return Appointment.objects.filter(id=self.kwargs.get('pk'), status='approved').first()
    
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
        

