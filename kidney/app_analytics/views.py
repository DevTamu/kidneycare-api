from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta, datetime
from app_appointment.models import Appointment
from kidney.utils import ResponseMessageUtils
from django.db.models.functions import TruncDate
from app_authentication.models import User, UserInformation
from django.db.models.aggregates import Count
from django.db.models.functions import ExtractMonth
from calendar import month_abbr

class GetPatientAnalyticsView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        try:
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
                    message = f"Patients increased by {abs(int(percent_change))}% in 7 days"
                else:
                    message = f"Patients decreased by {abs(int(percent_change))}% in 7 days"

            else:
                percent_change = 0  # or "N/A" if no baseline data
                growth_multiplier = 1.0

                # percent_change = round((calculate_diff_patients / this_week_patients) * 100, 2)
                # growth_multiplier = round(this_week_patients / last_week_patients, 3) 

                # if percent_change > 0:
                #     message = f"Patients increased by {abs(int(percent_change))}% in 7 days"
                # else:
                #     message = f"Patients decreased by {abs(int(percent_change))}% in 7 days"

            daily_appointments = (
                Appointment.objects
                .annotate(created_date=TruncDate('created_at'))
                .filter(created_date__range=[this_week_start, today])
                .values('created_date')
                .annotate(patient_count=Count('user_id', distinct=True))
                .order_by('created_date')
            )

            graph_data = []

            date_cursor = this_week_start

            while date_cursor <= today:
                entry_data = next((item for item in daily_appointments if item['created_date'] == date_cursor), None)
                count = entry_data['patient_count'] if entry_data else 0
                graph_data.append({
                    "value": count
                })
                date_cursor += timedelta(days=1)

            data = {
                'total_patients': this_week_patients,
                # 'change': float(calculate_diff_patients),
                'percent_change': abs(int(percent_change)) if percent_change else 0,
                'growth': growth_multiplier,
                "summary": message,
                "graph_data": graph_data
            }

            return ResponseMessageUtils(
                message="Analytics of Patient",
                data=data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

class GetAppointmentAnalyticsView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        try:
            message = None

            today = timezone.now().date()
            this_week_start = today - timedelta(days=6)
            last_week_start = this_week_start - timedelta(days=7)
            last_week_end = this_week_start - timedelta(days=1)
            

            this_week_appointments = (
                Appointment.objects
                .annotate(created_date=TruncDate('created_at'))
                .filter(created_date__range=[this_week_start, today])
                .values('id').count() 
            )

            last_week_appointments = (
                Appointment.objects
                .annotate(created_date=TruncDate('created_at'))
                .filter(created_date__range=[last_week_start, last_week_end]
                ).values('id').count()
            )

            calculate_diff_appointments = this_week_appointments - last_week_appointments


            if last_week_appointments > 0:

                percent_change = round((calculate_diff_appointments / last_week_appointments) * 100, 2)
                growth_multiplier = round(this_week_appointments / last_week_appointments, 3) 

                if percent_change > 0:
                    message = f"Appointment increased by {abs(int(percent_change))}% in 7 days."
                else:
                    message = f"Appointment decreased by {abs(int(percent_change))}% in 7 days."
            else:
                
                # percent_change = round((calculate_diff_appointments / this_week_appointments) * 100, 2)
                # growth_multiplier = round(this_week_appointments / last_week_appointments, 3) 

                # if percent_change > 0:
                #     message = f"Appointment increased by {abs(int(percent_change))}% in 7 days."
                # else:
                    # message = f"Appointment decreased by {abs(int(percent_change))}% in 7 days."
                percent_change = 0
                growth_multiplier = 1.0


            daily_appointments = (
                Appointment.objects
                .annotate(created_date=TruncDate('created_at'))
                .values('created_date')
                .filter(created_date__range=[this_week_start, today])
                .annotate(appointment_count=Count('id'))
                .order_by('created_date')
            )

            date_cursor = this_week_start
            graph_data = []

            while date_cursor <= today:
                entry_data = next((item for item in daily_appointments if item["created_date"] == date_cursor), None)
                count = entry_data["appointment_count"] if entry_data else 0
                graph_data.append({
                    "values": count
                })
                #increment the date cursor by 1 day
                date_cursor += timedelta(days=1)
            data = {
                'total_appointments': this_week_appointments,
                # 'change': abs(float(calculate_diff_appointments)),
                'percent_change': abs(int(percent_change)) if percent_change else 0,
                "growth": growth_multiplier,
                "summary": message,
                "graph_data": graph_data
            }

            return ResponseMessageUtils(
                message="Analytics of Appointments",
                data=data,
                status_code=status.HTTP_200_OK
            )
        
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class GetProviderAnalyticsView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        try:
            total_provider = User.objects.filter(role__in=['nurse', 'head nurse']).count()

            return ResponseMessageUtils(
                message="Analytics of Healthcare Provider",
                data={
                    "total_provider": total_provider
                },
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

class GetAppointmentStatusBreakdownView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        try:
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
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class GetPatientTrackingGenderView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):

        try:

            data_output = {}

            gender_month_counts = (
                UserInformation.objects.filter(user__role="patient")
                .annotate(month=ExtractMonth('created_at'))
                .values('gender', 'month')
                .annotate(count=Count('user_id'))
                .order_by('month')
            )

            data_labels = {
                "labels": [month_abbr[m] for m in range(1, 13)],
                "male": [0] * 12,
                "female": [0] * 12
            }
            

            for data in gender_month_counts:
                gender_value = str(data["gender"]).lower()
                month_index = data["month"] - 1

                if gender_value in data_labels:
                    data_labels[gender_value][month_index] = data["count"]

                #accumulate total count per gender
                if gender_value == "male":
                    data_output["male_tracking_data"] = {
                        "gender": gender_value,
                        "count": data_output.get("male", {}).get("count", 0) + data["count"]
                    }
                elif gender_value == "female":
                    data_output["female_tracking_data"] = {
                        "gender": gender_value,
                        "count": data_output.get("female", {}).get("count", 0) + data["count"]
                    }

            #merged the final results
            final_result = {**data_output, "patient_month_tracking_data": {**data_labels}}

            return ResponseMessageUtils(
                message="Patient Tracking",
                data=final_result,
                status_code=200
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

