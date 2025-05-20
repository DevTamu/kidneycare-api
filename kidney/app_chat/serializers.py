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

        #rename keys
        data["is_read"] = data.pop('read', None)
        data["chat_id"] = data.pop('id', None)
        data["sender_id"] = str(data.pop('sender', ""))
        data["receiver_id"] = str(data.pop('receiver', ""))

        #remove from the response
        data.pop('updated_at')

        return data
    

class GetNotificationChatsInProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'

    def to_representation(self, instance):

        data = super().to_representation(instance)

        #removed from the response
        data.pop('created_at')
        data.pop('updated_at')

        #rename keys
        data["sender_id"] = str(data.pop('sender')).replace("-", "")
        data["receiver_id"] = str(data.pop('receiver')).replace("-", "")
        data["chat_id"] = data.pop('id')

        return data
