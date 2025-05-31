from rest_framework import serializers
from .models import Notification
from datetime import datetime

class NotificationsInPatientSerializer(serializers.ModelSerializer):


    class Meta:
        model = Notification
        fields = '__all__'

    # def get_sent_at(self, obj):

    #     return timezone.make_aware(datetime.fromtimestamp(obj.sent_at))

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #removed from the response
        data.pop('created_at')
        data.pop('updated_at')

        # dt = datetime.fromisoformat(data.pop('sent_at'))

        # data["sent_at"] = dt.timestamp()

        #rename key
        data["appointment_id"] = data.pop('appointment')
        data["notification_id"] = data.pop('id')

        return data