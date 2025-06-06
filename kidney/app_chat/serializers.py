from rest_framework import serializers
from .models import Message
from app_authentication.models import Profile, User
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
from django.db import connection

    

class GetNotificationChatsToProviderSerializer(serializers.ModelSerializer):

    time_sent = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['content', 'sender', 'receiver', 'id', 'time_sent', 'read', 'status']

    def get_time_sent(self, obj):

        return timezone.localtime(getattr(obj, 'date_sent', None)).strftime('%I:%M %p')

    def to_representation(self, instance):

        data = super().to_representation(instance)

        #rename keys
        data["message"] = str(data.pop('content')).lower()
        data["sent"] = str(data.pop('status')).lower()
        data["sender_id"] = str(data.pop('sender'))
        data["receiver_id"] = str(data.pop('receiver'))
        data["chat_id"] = data.pop('id')

        return data
    

class UpdateNotificationChatInProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['id']

    def update(self, instance, validated_data):

        instance.read = True
        instance.save()

        return instance
    
# class UpdateChatStatusInPatientSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Message
#         fields = ['id']

#     def update(self, instance, validated_data):

#         instance.read = True
#         instance.save()

#         return instance
    

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
            "chat_id": int(data.pop('id'))
            
        }

        #rename key
        #removed from the response
        data.pop('sender')
        data.pop('receiver')
        data.pop('read')
        data.pop('status')
        data.pop('date_sent')
        data.pop('content')

        local_time = timezone.localtime(instance.date_sent)

        data.update(provider_information)
        data["last_message"] = {
            "provider_status": getattr(provider, 'status', 'offline').lower(),
            "provider_first_name": provider.first_name,
            "provider_image": getattr(getattr(provider, 'user_profile', None), 'picture', None).url if getattr(getattr(provider, 'user_profile', None), 'picture', None) else None,
            "provider_role": getattr(provider, 'role', None).lower(),
            "message": instance.content,
            "status": instance.status.lower(),
            "is_read": instance.read,
            "sender_id": str(instance.sender.id),
            "receiver_id": str(instance.receiver.id),
            "time_sent": local_time.strftime('%I:%M %p')
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
            "chat_id": int(data.pop('id'))
            # "role": getattr(patient, 'role', 'unknown').lower(),  
        }

        #rename key
        # data["chat_id"] = data.pop('id')

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
            "patient_first_name": patient.first_name,
            "patient_last_name": patient.last_name,
            "patient_image": getattr(getattr(patient, 'user_profile', None), 'picture', None).url if getattr(getattr(patient, 'user_profile', None), 'picture', None) else None,
            "patient_status": getattr(patient, 'status', 'offline').lower(),
            "message": instance.content,
            "message_status": instance.status.lower(),
            "is_read": instance.read,
            "sender_id": str(instance.sender.id),
            "receiver_id": str(instance.receiver.id),
            "time_sent": local_time.strftime('%I:%M %p')
        }

        return data
    

class GetPatientChatInformationSerializer(serializers.ModelSerializer):

    user_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'user_image', 'status']

    def get_user_image(self, obj):
        return getattr(getattr(obj, 'user_profile', None), 'picture', None).url if getattr(getattr(obj, 'user_profile', None), 'picture', None) else None
    
    def to_representation(self, instance):

        data = super().to_representation(instance)

        messages_list = None

        #rename key
        data["patient_id"] = data.pop('id')

        user_id = self.context.get('user_id')

        patient = User.objects.filter(id=instance.id, role='patient').first()

        if patient:

            admin = User.objects.filter(id=user_id, role='admin').first()

            messages = Message.objects.select_related('sender', 'receiver').filter(
                sender=patient, receiver=admin
            ).values('content', 'status', 'sender', 'receiver', 'date_sent', 'read', 'id').union(
                Message.objects.select_related('sender', 'receiver').filter(
                    (
                        Q(sender=patient, receiver=admin) |
                        Q(sender=admin, receiver=patient)
                    )
                ).values('content', 'status', 'sender', 'receiver', 'date_sent', 'read', 'id')
            )

            messages_list = [{

                "message": str(message["content"]).lower(),
                "sent": str(message["status"]).lower(),
                "is_read": message["read"],
                "sender_id": str(message["sender"]),
                "receiver_id": str(message["receiver"]),
                "chat_id": int(message["id"]),
                "time_sent": timezone.localtime(message["date_sent"]).strftime("%I:%M")

            }for message in messages]

            data["messages"] = messages_list

        return data

        

class GetProviderChatInformationSerializer(serializers.ModelSerializer):

    user_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'user_image', 'status', 'role']

    def to_representation(self, instance):

        user_id = self.context.get('user_id')

        data = super().to_representation(instance)
        
        #rename keys
        data["provider_id"] = str(data.pop('id'))
        data["provider_first_name"] = data.pop('first_name')
        data["provider_status"] = str(data.pop('status')).lower()
        # data["provider_last_name"] = data.pop('last_name')
        data["provider_image"] = data.pop('user_image')
        data["provider_role"] = data.pop('role')

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
                ).values('content', 'status', 'sender', 'receiver', 'date_sent', 'read', 'id').union(
                    Message.objects.prefetch_related('sender', 'receiver').filter(
                        (
                            Q(sender=provider, receiver=patient) |
                            Q(sender=patient, receiver=provider)
                        )
                    ).values(
                        'content', 'status', 'sender', 'receiver', 'date_sent', 'read', 'id'
                    )
                )  

                messages_list = [{
                    "message": str(message["content"]).lower(),
                    "sent": str(message["status"]).lower(),
                    "is_read": message["read"],
                    "sender_id": str(message["sender"]),
                    "receiver_id": str(message["receiver"]),
                    "chat_id": int(message["id"]),
                    "time_sent": timezone.localtime(message["date_sent"]).strftime('%I:%M')
                } for message in messages]

        data["messages"] = messages_list

        return data

    def get_user_image(self, obj):
        return getattr(getattr(obj, 'user_profile', None), 'picture', None).url if getattr(getattr(obj, 'user_profile', None), 'picture', None) else None


    



    
