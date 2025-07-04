from rest_framework import serializers
from .models import Notification
from datetime import datetime
from app_appointment.models import AssignedProvider

class NotificationsInPatientSerializer(serializers.ModelSerializer):

    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'title', 'image', 'description', 'is_read', 'date', 'time', 'appointment']

    def get_date(self, obj):
        return getattr(obj, 'created_at', None).strftime("%m/%d/%Y")
    
    def get_time(self, obj):
        return getattr(obj, 'created_at', None).strftime("%I:%M %p")
    
    def get_title(self, obj):

        appointment_status =  getattr(obj.appointment, "status")

        if appointment_status == "cancelled":
            return f"Appointment Declined"
        elif appointment_status == "rescheduled":
            return f"Machine Under Maintenance"
        else:
            status = getattr(obj.appointment, "status", None)
            return f"Appointment {str(status[0]).upper()}{status[1:]}"
    
    def get_image(self, obj):

        assigned_appointment = getattr(obj.appointment, "id", None)

        try:
            assigned_provider = AssignedProvider.objects.get(assigned_patient_appointment=assigned_appointment)
        except AssignedProvider.DoesNotExist:
            assigned_provider = None


        return (
            getattr(getattr(getattr(assigned_provider, 'assigned_provider', None), 'user_profile', None), 'picture', None).url
            if getattr(getattr(getattr(assigned_provider, 'assigned_provider', None), 'user_profile', None), 'picture', None)
            else None
        )
    
    def get_description(self, obj):

        appointment_status =  getattr(obj.appointment, "status")

        if appointment_status == "approved":
            return "Congratulations - your apppointment is confirmed! We’re looking forward to meeting with you."
        elif appointment_status == "cancelled":
            return "Your appointment request has been declined. Please reschedule or choose a different time."
        elif appointment_status == "rescheduled":
            return "Maintenance is currently in progress. Please reschedule your appointment. We apologize for any inconvenience caused."

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #rename key
        data["appointment_id"] = data.pop('appointment')

        return data