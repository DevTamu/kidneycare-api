from rest_framework import serializers
from .models import Notification

class NotificationsInPatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'
