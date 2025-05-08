from rest_framework import serializers
from .models import Message


class GetUsersMessageSerializer(serializers.ModelSerializer):
    
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'

    #convert created_at to a readable time-format
    def get_created_at(self, obj):
        return obj.created_at.strftime("%I:%M")

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #rename and clean up fields safely
        data["is_read"] = data.pop('read', None)
        data["chat_id"] = data.pop('id', None)

        data.pop('updated_at')
        
        data["sender_id"] = str(data.pop('sender', ""))
        data["receiver_id"] = str(data.pop('receiver', ""))

        return data

    
