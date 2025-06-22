from rest_framework import serializers
from .models import Message
from app_authentication.models import Profile, User
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
from django.db import connection
from kidney.pagination.appointment_pagination import Pagination
    

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
        fields = ['id', 'sender', 'receiver', 'content', 'read', 'status', 'date_sent', 'image']

    def to_representation(self, instance):
        request = self.context.get('request')
        data = super().to_representation(instance)
        pk = self.context.get('pk')

        provider = instance.sender if str(instance.sender.id) != str(pk) else instance.receiver

        provider_information = {
            "provider_id": provider.id,
            "chat_id": int(data.pop('id'))
        }

        #removed from the response
        data.pop('sender')
        data.pop('receiver')
        data.pop('read')
        data.pop('status')
        data.pop('date_sent')
        data.pop('content')
        data.pop('image')

        data.update(provider_information)
        data["last_message"] = {
            "provider_first_name": provider.first_name,
            "provider_status": getattr(provider, 'status', 'offline').lower(),
            "provider_image": request.build_absolute_uri(getattr(getattr(provider, 'user_profile', None), 'picture', None).url) if getattr(getattr(provider, 'user_profile', None), 'picture', None) else None,
            "message": instance.content,
            "message_status": instance.status.lower(),
            "is_read": instance.read,
            "image": str(instance.image.url) if instance.image else None,
            "sender_id": str(instance.sender.id),
            "receiver_id": str(instance.receiver.id),
            "created_at": str(instance.created_at)
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
            "id": int(data.pop('id'))
        }

        #removed from the response
        data.pop('sender')
        data.pop('receiver')
        data.pop('read')
        data.pop('status')
        data.pop('date_sent')
        data.pop('content')

        local_time = timezone.localtime(instance.date_sent)

        data.update(patient_information)
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
            "created_at": str(instance.created_at),
            "image": str(instance.image)
        }

        return data
    

class UpdateChatStatusInAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id']

    def update(self, instance, validated_data):        

        sender_id = self.context.get('sender_id')
        receiver_id = self.context.get('receiver_id')

        Message.objects.filter(
           Q(sender=sender_id, receiver=receiver_id) |
           Q(sender=receiver_id, receiver=sender_id)
        ).update(read=True, status='read')

        return instance


class GetPatientChatInformationSerializer(serializers.ModelSerializer): 

    user_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'user_image', 'status']

    def get_user_image(self, obj):
        return getattr(getattr(obj, 'user_profile', None), 'picture', None).url if getattr(getattr(obj, 'user_profile', None), 'picture', None) else None
    
    def to_representation(self, instance):

        paginator = Pagination()

        data = super().to_representation(instance)

        request = self.context.get('request')

        messages_list = []
        pagination_messages_list = []

        #rename key
        data["patient_id"] = data.pop('id')

        user_id = self.context.get('user_id')

        patient = User.objects.filter(id=instance.id, role='patient').first()

        if patient:

            admin = User.objects.filter(id=user_id, role='admin').first()

            messages = Message.objects.select_related('sender', 'receiver').filter(
                sender=patient, receiver=admin
            ).values('content', 'status', 'sender', 'receiver', 'created_at', 'read', 'id', 'image').union(
                Message.objects.select_related('sender', 'receiver').filter(
                    (
                        Q(sender=patient, receiver=admin) |
                        Q(sender=admin, receiver=patient)
                    )
                ).values('content', 'status', 'sender', 'receiver', 'created_at', 'read', 'id', 'image')
            ).order_by('-created_at')

            messages_list = [{
                "id": int(message["id"]),
                "message": str(message["content"]).lower(),
                "message_status": str(message["status"]).lower(),
                "is_read": message["read"],
                "sender_id": str(message["sender"]),
                "receiver_id": str(message["receiver"]),
                "created_at": str(message["created_at"]),
                "image": request.build_absolute_uri(message["image"]) if message["image"] else None
            }for message in messages]
            
            pagination_messages_list = paginator.paginate_queryset(messages_list, request)

            data["count"] = paginator.page.paginator.count if pagination_messages_list else 0
            data["next"] = paginator.get_next_link() if pagination_messages_list else None
            data["previous"] = paginator.get_previous_link() if pagination_messages_list else None
            data["first_name"] = data.pop('first_name')
            data["last_name"] = data.pop('last_name')
            data["user_image"] = data.pop('user_image')
            data["status"] = data.pop('status')
            data["patient_id"] = data.pop('patient_id')

            data["messages"] = pagination_messages_list


        return data


class GetProviderChatInformationSerializer(serializers.ModelSerializer):

    user_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'user_image', 'status']

    def to_representation(self, instance):
        
        user_id = self.context.get('user_id')
        #get the request object from the serializer context
        request  = self.context.get('request')

        data = super().to_representation(instance)
        
        paginator = Pagination()

        #get the patient as a single object
        patient = User.objects.filter(id=user_id, role='patient').first()

        messages_list = []
        paginated_messages = []

        if patient:
            #get the provider as a single object
            provider = User.objects.filter(id=instance.id, role__in=['nurse', 'head nurse']).first()

            if provider:

                #get all messages between the patient and provider
                messages = Message.objects.prefetch_related('sender', 'receiver').filter(
                    sender=patient, receiver=provider
                ).union(
                    Message.objects.prefetch_related('sender', 'receiver').filter(
                        (
                            Q(sender=provider, receiver=patient) |
                            Q(sender=patient, receiver=provider)
                        )
                    )
                ).order_by('-created_at')

                messages_list = [{
                    "message": str(message.content).lower(),
                    "message_status": str(message.status).lower(),
                    "is_read": message.read,
                    "image": str(message.image.url) if message.image else None,
                    "chat_id": int(message.id),
                    "sender_id": str(message.sender.id),
                    "receiver_id": str(message.receiver.id),
                    "created_at": str(message.created_at)
                } for message in messages]

            paginated_messages = paginator.paginate_queryset(messages_list, request)

        data["count"] = paginator.page.paginator.count if paginated_messages else 0
        data["provider_id"] = str(data.pop('id'))
        data["provider_first_name"] = data.pop('first_name')
        data["provider_status"] = str(data.pop('status')).lower()
        data["provider_image"] = data.pop('user_image')
        data["messages"] = paginated_messages


        return data

    def get_user_image(self, obj):
        return getattr(getattr(obj, 'user_profile', None), 'picture', None).url if getattr(getattr(obj, 'user_profile', None), 'picture', None) else None
    



