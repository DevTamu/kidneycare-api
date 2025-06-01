from rest_framework import serializers
from .models import Message
from app_authentication.models import Profile, User
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
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
    

class GetUsersChatSerializer(serializers.ModelSerializer):
    
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'

    def get_created_at(self, obj):

        created_at = obj.created_at

        return created_at.strftime('%I:%M %p')

    def to_representation(self, instance):

        #get the default serialized data from the parent class
        data = super().to_representation(instance)

        #get the request object from the serializer context
        request = self.context.get('request')

        sender_id = data.pop('sender')
        receiver_id = data.pop('receiver')

        user_profile = Profile.objects.select_related('user').filter(user=sender_id)

        for user in user_profile.all():

            data["first_name"] = user.user.first_name
            data["last_name"] = user.user.last_name
            data["picture"] = request.build_absolute_uri(user.picture.url) if user.picture else None

        #removed from the response
        data.pop('updated_at')

        #rename keys
        data["time_sent"] = data.pop('created_at')
        data["sender_id"] = str(sender_id)
        data["receiver_id"] = str(receiver_id)
        data["chat_id"] = data.pop('id')

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
            "user_image": provider.profile.picture.url if hasattr(provider, 'profile') and provider.profile.picture else None
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
            "time_sent": local_time.strftime('%I:%M %p')
        }

        return data

    
        return data
    



    
