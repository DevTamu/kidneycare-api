from rest_framework import serializers
from .models import Message
from app_authentication.models import Profile, User
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
from django.db import connection
import pprint
class GetUsersMessageSerializer(serializers.ModelSerializer):
    
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'

    #convert created_at to a readable time-format
    def get_created_at(self, obj):
        return obj.created_at.strftime("%I:%M: %p")

    def to_representation(self, instance):

        data = super().to_representation(instance)

        #rename keys
        data["is_read"] = str(data.pop('read', None)).lower()
        data["chat_id"] = data.pop('id', None)
        data["sender_id"] = str(data.pop('sender'))
        data["receiver_id"] = str(data.pop('receiver'))

        #remove from the response
        data.pop('updated_at')

        return data
    

class GetNotificationChatsToProviderSerializer(serializers.ModelSerializer):

    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M %p', input_formats=['%Y-%m-%d %H:%M %p'])

    class Meta:
        model = Message
        fields = '__all__'

    def to_representation(self, instance):

        data = super().to_representation(instance)

        #removed from the response
        data.pop('updated_at')

        #rename keys
        data["sender_id"] = str(data.pop('sender'))
        data["receiver_id"] = str(data.pop('receiver'))
        data["chat_id"] = data.pop('id')
        data["created_at"] = str(data.pop('created_at'))[10:].strip()

        return data
    

class GetProvidersChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'read', 'status', 'date_sent']

    def to_representation(self, instance):
        request = self.context.get('request')
        data = super().to_representation(instance)
        pk = self.context.get('pk')

        provider = instance.sender if str(instance.sender.id) != str(pk) else instance.receiver

        provider_information = {
            "provider_id": provider.id,
            "role": getattr(provider, 'role', 'unknown').lower(),
            "status": getattr(provider, 'status', 'offline').lower(),
            "first_name": provider.first_name,
            "user_image": getattr(getattr(provider, 'user_profile', None), 'picture', None).url if getattr(getattr(provider, 'user_profile', None), 'picture', None) else None
        }

        #rename key
        data["chat_id"] = data.pop('id')

        #removed from the response
        data.pop('sender')
        data.pop('receiver')
        data.pop('read')
        data.pop('status')
        data.pop('date_sent')

        local_time = timezone.localtime(instance.date_sent)

        data.update(provider_information)
        data["last_message"] = {
            "message": instance.content,
            "status": instance.status.lower(),
            "is_read": instance.read,
            "sender_id": str(instance.sender.id),
            "receiver_id": str(instance.receiver.id),
            "time_sent": local_time.strftime('%I:%M')
        }

        return data
    

class GetPatientsChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'read', 'status', 'date_sent']

    def to_representation(self, instance):
        request = self.context.get('request')
        data = super().to_representation(instance)
        pk = self.context.get('pk')

        patient = instance.sender if str(instance.sender.id) != str(pk) else instance.receiver

        patient_information = {
            "patient_id": patient.id,
            # "role": getattr(patient, 'role', 'unknown').lower(),  
        }

        #rename key
        data["chat_id"] = data.pop('id')

        #removed from the response
        data.pop('sender')
        data.pop('receiver')
        data.pop('read')
        data.pop('status')
        data.pop('date_sent')
        data.pop('content')

        local_time = timezone.localtime(instance.date_sent)

        data.update(patient_information )
        data["latest_message"] = {
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "user_image": getattr(getattr(patient, 'user_profile', None), 'picture', None).url if getattr(getattr(patient, 'user_profile', None), 'picture', None) else None,
            "status": getattr(patient, 'status', 'offline').lower(),
            "message": instance.content,
            "message_status": instance.status.lower(),
            "is_read": instance.read,
            "sender_id": str(instance.sender.id),
            "receiver_id": str(instance.receiver.id),
            "time_sent": local_time.strftime('%I:%M')
        }

        return data
    

class GetPatientChatInformationSerializer(serializers.ModelSerializer):

    user_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'user_image']

    def get_user_image(self, obj):
        return getattr(getattr(obj, 'user_profile', None), 'picture', None).url if getattr(getattr(obj, 'user_profile', None), 'picture', None) else None
    

class GetProviderChatInformationSerializer(serializers.ModelSerializer):

    user_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'user_image']

    def to_representation(self, instance):

        user_id = self.context.get('user_id')

        data = super().to_representation(instance)

        #rename keys
        data["provider_id"] = str(data.pop('id'))
        data["provider_first_name"] = data.pop('first_name')
        data["provider_last_name"] = data.pop('last_name')
        data["provider_image"] = data.pop('user_image')

        #get the patient as a single object
        patient = User.objects.filter(id=user_id, role='patient').first()

        messages_list = None

        if patient:
            #get the provider as a single object
            provider = User.objects.filter(id=instance.id, role__in=['nurse', 'head nurse']).first()

            if provider:

                #get all messages between the patient and provider
                messages = Message.objects.prefetch_related('sender', 'receiver').filter(
                    sender=patient, receiver=provider
                ).values('content', 'status', 'sender', 'receiver', 'date_sent').union(
                    Message.objects.prefetch_related('sender', 'receiver').filter(sender=provider, receiver=patient).values(
                        'content', 'status', 'sender', 'receiver', 'date_sent'
                    )
                )  

                messages_list = [{
                    "message": str(message["content"]).lower(),
                    "sent": str(message["status"]).lower(),
                    "sender_id": str(message["sender"]),
                    "receiver_id": str(message["receiver"]),
                    "time_sent": timezone.localtime(message["date_sent"]).strftime('%I:%M')
                } for message in messages]

        data["messages"] = messages_list

        return data

    def get_user_image(self, obj):
        return getattr(getattr(obj, 'user_profile', None), 'picture', None).url if getattr(getattr(obj, 'user_profile', None), 'picture', None) else None


    



    
