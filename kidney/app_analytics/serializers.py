from app_authentication.models import User
from app_appointment.models import Appointment
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

#get todays date
today = timezone.now().date()

class GetPatientAnalyticsSerializer(serializers.Serializer):

    def to_representation(self, instance):

        #get the request from the context
        request = self.context.get('request')

        data = super().to_representation(instance)

        this_week_start = today - timedelta(days=6)  # 7-day window including today
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = this_week_start - timedelta(days=1)

        this_week_patients = User.objects.filter(
            created_at__date__range=[this_week_start, today]
        ).values('id').distinct().count()

        print(f"qwewqe: {this_week_patients}")

        return data
        



