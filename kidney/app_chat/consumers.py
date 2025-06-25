import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from kidney.utils import get_user_by_id, get_base64_file_size, get_absolute_image_url
from app_authentication.models import User
from django.utils import timezone
from asgiref.sync import sync_to_async
import uuid
import base64
from django.core.files.base import ContentFile
from app_chat.models import Message
import logging

logger = logging.getLogger(__name__)

class BaseChatConsumer(AsyncWebsocketConsumer):
    async def send_json(self, data: dict):
        await self.send(text_data=json.dumps(data))

    async def inbox_update(self, event):
        print(f"[INBOX_CONSUMER] Sent to user inbox: {event['receiver_id']} or {event['sender_id']}")
        await self.send_json({
            "status": event["status"],
            "first_name": event["first_name"],
            "user_image": event["user_image"],
            "message": event["message"],
            "message_status": event["message_status"],
            "read": event["read"],
            "chat_id": event["chat_id"],
            "sender_id": str(event["sender_id"]),
            "receiver_id": str(event["receiver_id"]),
            "created_at": event["created_at"],
            "image": event["image"]
        })

    async def notification(self, event):
        await self.send_json({
            "first_name": event["first_name"],
            "last_name": event["last_name"],
            "status": event["status"],
            "message": event["message"],
            "created_at": event["created_at"],
            "picture": event["picture"],
            "message_status": event["message_status"]
        })

    async def get_status(self, event):
        await self.send_json({
            "status": event["is_online"],
        })



class ChatConsumer(BaseChatConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None

    async def connect(self):
        user = self.scope["user"]
        if not user:
            await self.close(code=4003)
            return

        self.chat_type = self.scope["url_route"]["kwargs"]["chat_type"]
        self.receiver_id = self.scope["url_route"]["kwargs"]["room_name"]
        self.sender_id = str(user.id)

        self.room_group_name = f"chat_{self.chat_type}_{min(self.receiver_id, self.sender_id)}_{max(self.receiver_id, self.sender_id)}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        receiver = await self.get_user(self.receiver_id)
        await self.get_user_status(user, receiver)

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return await self.send_json({"error": "Invalid JSON"})

        message = await self.save_message(data.get("message"), data.get("image_data"))
        if message:
            await self.send_to_room(message)
            await self.send_to_inbox(message)

    async def send_to_room(self, message):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message.content,
                "sender_id": str(message.sender.id),
                "receiver_id": str(message.receiver.id),
                "chat_id": message.id,
                "created_at": str(message.created_at),
                "message_status": message.status,
                "image": message.image.url if message.image else None
            }
        )

    async def chat_message(self, event):
        await self.send_json(event)

    async def get_user_status(self, sender, receiver):
        await self.channel_layer.group_send(
            f"user_{sender.id}",
            {
                "type": "get_status",
                "is_online": str(receiver.status).lower(),
            }
        )

    async def send_to_inbox(self, message):
        sender = message.sender
        receiver = message.receiver

        async def send_to(user, other_user):
            profile_url = await self.get_profile(other_user)
            await self.channel_layer.group_send(
                f"user_{user.id}",
                {
                    "type": "inbox_update",
                    "status": str(other_user.status).lower(),
                    "first_name": other_user.first_name,
                    "user_image": profile_url,
                    "message": message.content,
                    "message_status": message.status,
                    "read": message.read,
                    "chat_id": message.id,
                    "sender_id": str(message.sender.id),
                    "receiver_id": str(message.receiver.id),
                    "created_at": str(message.created_at),
                    "image": message.image.url if message.image else None
                }
            )

        # Logic for roles
        if sender.role == "patient" and receiver.role == "admin":
            # inbox should go to BOTH
            await send_to(sender, receiver)
            await send_to(receiver, sender)

        elif sender.role == "admin" and receiver.role == "patient":
            # inbox should go to BOTH
            await send_to(sender, receiver)
            await send_to(receiver, sender)

        elif (
            sender.role == "patient" and receiver.role in ["nurse", "head_nurse"]
        ) or (
            sender.role in ["nurse", "head_nurse"] and receiver.role == "patient"
        ):
            # always send to patient only
            patient = sender if sender.role == "patient" else receiver
            nurse_or_sender = receiver if sender.role == "patient" else sender
            await send_to(patient, nurse_or_sender)


        if sender.role == "patient" and receiver.role in ["nurse", "head_nurse"]:
            await self.send_notification(sender, receiver, message)

    async def send_notification(self, sender, receiver, message):
        profile = await self.get_profile(sender)
        await self.channel_layer.group_send(
            f"user_{receiver.id}",
            {
                "type": "notification",
                "first_name": sender.first_name,
                "last_name": sender.last_name,
                "status": str(sender.status).lower(),   
                "message": message.content,
                "created_at": str(message.created_at),
                "picture": profile,
                "message_status": message.status
            }
        )

    async def save_message(self, message_content=None, image_data=None):
        receiver = await self.get_user(self.receiver_id)
        sender = await self.get_user(self.sender_id)

        if not receiver or not sender:
            await self.send_json({"error": "Could not fetch users."})
            return

        message = Message(
            sender=sender,
            receiver=receiver,
            content=message_content,
            status='sent',
            date_sent=timezone.now()
        )

        if image_data:
            try:
                if get_base64_file_size(image_data) / (1024 * 1024) >= 20:
                    await self.send_json({"error": "Image too large."})
                    return
                format, img_str = image_data.split(';base64,')
                ext = format.split('/')[-1]
                message.image = ContentFile(base64.b64decode(img_str), name=f"{uuid.uuid4()}.{ext}")
            except Exception:
                await self.send_json({"error": "Failed to decode image."})
                return

        await sync_to_async(message.save)()
        return message

    async def get_user(self, user_id) -> User:
        return await get_user_by_id(user_id)

    @sync_to_async
    def get_profile(self, user):
        from app_authentication.models import Profile
        try:
            profile = Profile.objects.get(user=user)
            return profile.picture.url if profile.picture else None
        except Profile.DoesNotExist:
            return None




class InboxConsumer(BaseChatConsumer):
    async def connect(self):
        user = self.scope["user"]
        self.inbox_group_name = f"user_{user.id}"
        print(f"[InboxConsumer CONNECTED] user={user.id} inbox_group={self.inbox_group_name}")
        await self.channel_layer.group_add(self.inbox_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'inbox_group_name'):
            await self.channel_layer.group_discard(self.inbox_group_name, self.channel_name)


class NotificationConsumer(BaseChatConsumer):
    pass

