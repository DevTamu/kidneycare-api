from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
# from .serializers import (
#     GetPatientAnalyticsSerializer
# )
from django.utils import timezone
from datetime import timedelta
from app_appointment.models import Appointment
from kidney.utils import ResponseMessageUtils
from django.db.models.functions import TruncDate
from app_authentication.models import User
from django.db.models.aggregates import Count

class GetPatientAnalyticsView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        message = None

        today = timezone.now().date()
        this_week_start = today - timedelta(days=6)
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = this_week_start - timedelta(days=1)

        this_week_patients = (
            Appointment.objects
            .annotate(created_date=TruncDate('created_at'))
            .filter(created_date__range=[this_week_start, today])
            .values('user_id').distinct().count() 
        )

        last_week_patients = (
            Appointment.objects
            .annotate(created_date=TruncDate('created_at'))
            .filter(created_date__range=[last_week_start, last_week_end])
            .values('user_id').distinct().count() 
        )

        # Calculate changes
        calculate_diff_patients = this_week_patients - last_week_patients

        if last_week_patients > 0:
            percent_change = round((calculate_diff_patients / last_week_patients) * 100, 2)
            growth_multiplier = round(this_week_patients / last_week_patients, 3) 

            if percent_change > 0:
                message = f"Patients increased by {abs(percent_change)}% in 7 days"
            else:
                message = f"Patients decreased by {abs(percent_change)}% in 7 days"

        else:
            percent_change = 0  # or "N/A" if no baseline data
            growth_multiplier = 1.0


        data = {
            'total_patient': this_week_patients,
            'change': float(calculate_diff_patients),
            'percent_change': int(percent_change) if percent_change else 0,
            'growth': growth_multiplier,  # New: Added multiplier,
            "summary": message
        }

        return ResponseMessageUtils(
            message="Analytics of Patient",
            data=data,
            status_code=status.HTTP_200_OK
        )
    

class GetAppointmentAnalyticsView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        message = None

        today = timezone.now().date()
        this_week_start = today - timedelta(days=6)
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = this_week_start - timedelta(days=1)
        
        this_week_appointments = (
            Appointment.objects
            .annotate(created_date=TruncDate('created_at'))
            .filter(created_date__range=[this_week_start, today])
            .values('id').distinct().count() 
        )

        last_week_appointments = (
            Appointment.objects
            .annotate(created_date=TruncDate('created_at'))
            .filter(created_date__range=[last_week_start, last_week_end]
            ).values('id').distinct().count()
        )

        calculate_diff_patients = this_week_appointments - last_week_appointments

        if last_week_appointments > 0:
            percent_change = round((calculate_diff_patients / last_week_appointments) * 100, 2)
            growth_multiplier = round(this_week_appointments / last_week_appointments, 3) 
            if percent_change > 0:
                message = f"Appointment increase by {abs(percent_change)}% in 7 days."
            else:
                message = f"Appointment decreased by {abs(percent_change)}% in 7 days."
        else:
            percent_change = 0
            growth_multiplier = 1.0


        data = {
            'total_appointments': this_week_appointments,
            'change': float(calculate_diff_patients),
            'percent_change': percent_change if percent_change else 0,
            "growth": growth_multiplier,
            "summary": message
        }

        return ResponseMessageUtils(
            message="Analytics of Appointments",
            data=data,
            status_code=status.HTTP_200_OK
        )
    
class GetProviderAnalyticsView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        total_provider = User.objects.filter(role__in=['Nurse', 'Head Nurse']).count()

        return ResponseMessageUtils(
            message="Analytics of Healthcare Provider",
            data={
                "total_provider": total_provider
            },
            status_code=status.HTTP_200_OK
        )
    

class GetAppointmentStatusBreakdownView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        total_appointments = Appointment.objects.count()

        #initialize default data
        data = {}

        if total_appointments > 0:
            #get counts for each status
            status_counts = (
                Appointment.objects
                .values('status')
                .annotate(count=Count('id'))
            )

            #convert to percentage format
            for item in status_counts.all():
                status = item["status"]
                percentage = round((item["count"] / total_appointments) * 100, 2)
                data[f"percentage_{str(status.lower()).replace('-', '_')}_appointment"] = percentage
        else:
            #no appointments: set all to 0%
            statuses = ['pending', 'approved', 'check_in', 'in_progress', 'completed', 'cancelled', 'no_show', 'rescheduled']
            for status in statuses:
                data[f"percentage_{str(status).replace('-', '_')}_appointment"] = 0
        return ResponseMessageUtils(
            message="Analytics of Appointment status breakdown",
            data=data,
            status_code=200
        )