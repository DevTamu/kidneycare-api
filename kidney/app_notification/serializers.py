from rest_framework import serializers
from .models import Notification

class NotificationsInPatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #removed from the response
        data.pop('created_at')
        data.pop('updated_at')

        #capitalized the status
        data["status"] = str(data.pop('status')).capitalize()

        #rename key
        data["appointment_id"] = data.pop('appointment')
        data["notification_id"] = data.pop('id')

        return data