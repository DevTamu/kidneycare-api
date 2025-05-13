from app_authentication.models import User
from app_appointment.models import Appointment
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate
from kidney.utils import ResponseMessageUtils
from rest_framework import status

class GetPatientAnalyticsSerializer(serializers.Serializer):

    def to_representation(self, instance):
        print("to_representation called!")  # debug
        #get the request from the context
        request = self.context.get('request')
        data = super().to_representation(instance)

        today = timezone.now().date()
        this_week_start = today - timedelta(days=6)  # 7-day window including today
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = this_week_start - timedelta(days=1)

        this_week_patients = Appointment.objects.annotate(
            created_date=TruncDate('created_at')
        ).filter(
            created_date__range=[this_week_start, today]
        ).values('user_id').count()

        print(f"THIS WEEK PATIENT: {this_week_patients}")

        last_week_patients = Appointment.objects.annotate(
            created_date=TruncDate('created_at')
        ).filter(
            created_date__range=[last_week_start, last_week_end]
        ).values('user_id').count()

        print(f"LAST WEEK PATIENT: {last_week_patients}")

        #calculate difference and percentage
        change = this_week_patients - last_week_patients
        print(f"CHANGE: {change}")
        percent_change  = round((change / last_week_patients) * 100, 2) if last_week_patients > 0 else 100

        data = {
            'patient_total': this_week_patients,
            'change': change,
            'percent_change': percent_change
        }
        
        return ResponseMessageUtils(message="Analytics of Patient", data=data, status_code=status.HTTP_200_OK)



