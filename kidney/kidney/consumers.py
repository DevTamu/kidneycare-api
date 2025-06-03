import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .utils import get_user_by_id, get_base64_file_size
from app_authentication.models import User
from django.utils import timezone
from app_chat.models import Message
from asgiref.sync import sync_to_async
import uuid
import base64
from django.core.files.base import ContentFile

class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None
        self.inbox_group_name = None

    async def connect(self):
        """Handles the WebSocket connection."""
        try:
            #user is already authenticated by middleware
            user = self.scope["user"]
            if not user:
                await self.close(code=4003)
                return
            
            self.receiver_id = str(self.scope["url_route"]["kwargs"]["room_name"])
            self.sender_id = str(user.id)

            #create chat room and join the chat room
            self.room_group_name = f"chat_{min(self.receiver_id, self.sender_id)}_{max(self.receiver_id, self.sender_id)}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            #create sender inbox room and join the sender inbox group
            self.sender_inbox_name = f"user_{self.sender_id}"
            await self.channel_layer.group_add(self.sender_inbox_name, self.channel_name)

            #create receiver inbox room and join the receiver inbox group
            self.receiver_inbox_name = f"user_{self.receiver_id}"
            await self.channel_layer.group_add(self.receiver_inbox_name, self.channel_name)

            #accept the connection
            await self.accept()

            user_receiver = await get_user_by_id(self.receiver_id)
            await self.send_message_introduction(user, user_receiver)
            
        except Exception as e:
            await self.close(code=4003)
        

    async def disconnect(self, close_code):
        """Handles the WebSocket disconnection."""
        try:
            if hasattr(self, 'room_group_name') and self.room_group_name:
                await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            if hasattr(self, 'sender_inbox_name') and self.sender_inbox_name:
                await self.channel_layer.group_discard(self.inbox_group_name, self.channel_name)
            if hasattr(self, 'receiver_inbox_name') and self.receiver_inbox_name:
                await self.channel_layer.group_discard(self.receiver_inbox_name, self.channel_name)
        except Exception as e:
            print(f"[ERROR] Disconnect failed: {e}")

    async def receive(self, text_data):
        
        """Handles incoming messages from the WebSocket."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON data."}))
            return
        
        # update the database when the client reads the message by calling mark_message_as_read
        if data.get('type') == "message_read":
            message_id = data.get("message_id")
            if message_id:
                await self.mark_message_as_read(message_id)
            return
        

        image_data = data.get("image_data", None)
        
        message_content = data["message"]
        #if message not provided
        if not message_content:
            await self.send(text_data=json.dumps({"error": "Message is required."}))
            return
        
        #get the returned message from the save_message
        message_obj = await self.save_message(
            message_content=message_content,
            image_data=image_data
        )

        if message_obj:
            await self.send_message(message_obj)
            await self.send_message_to_inbox(message_obj)


    async def send_message(self, message):
        #send to chat room
        await self.channel_layer.group_send(
            self.room_group_name, #send to the receiver websocket
            {
                "type": "chat_message", 
                "message": message.content,
                "sender_id": str(message.sender.id),
                "receiver_id": str(message.receiver.id),
                "chat_id": None if message.sender.role == "patient" and message.receiver.role == "admin" or message.sender.role == "admin" and message.receiver.role == "patient" else int(message.id),
                "date_sent": timezone.localtime(message.date_sent).strftime('%I:%M'),
                "status": str(message.status).lower(),
                "image": message.image.url if message.image else None
            }
        )


    #receive message from room group
    async def chat_message(self, event): 
        """Handles broadcasting of the chat message to the WebSocket."""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": event["message"], #message content
            "sender_id": str(event["sender_id"]),
            "receiver_id": str(event["receiver_id"]),
            "chat_id": event["chat_id"],
            "date_sent": event["date_sent"],
            "status": event["status"],
            "image": event["image"]
        }))

    async def send_message_introduction(self, sender, receiver):
        

        if sender.role == "patient" and receiver.role == "admin":
            await self.channel_layer.group_send(
                self.room_group_name,
                {   
                    'type': 'chat_message_introduction',
                    'message': f"Hi {sender.first_name} {sender.last_name}, this is {receiver.first_name} from Boho Renal Care. I'd be happy to assist you",
                    "sender_id": str(sender.id),
                    "receiver_id": str(receiver.id)  
                }
            )
        elif sender.role == "admin" and receiver.role == "patient":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message_introduction',
                    'message': f"Hi {receiver.first_name} {receiver.last_name}, this is {sender.first_name} from Boho Renal Care. I'd be happy to assist you",
                    "sender_id": str(sender.id),
                    "receiver_id": str(receiver.id)  
                }
            )

    async def chat_message_introduction(self, event):
        await self.send(text_data=json.dumps({
            "introduction_message": event['message'],
            "sender_id": str(event['sender_id']),
            "receiver_id": str(event['receiver_id']),
        }))

    async def inbox_update(self, event):
        await self.send(text_data=json.dumps({
            "id": event["id"],
            "role": event["role"],
            "status": event["status"],
            "first_name": event["first_name"],
            "user_image": event["user_image"],
            "message": event["message"],
            "message_status": event["message_status"],
            "read": event["read"],
            "chat_id": event["chat_id"],
            "sender_id": str(event["sender_id"]),
            "receiver_id": str(event["receiver_id"]),
            "time_sent": event["time_sent"]
        }))

    async def send_message_to_inbox(self, message):

        receiver_user_id = str(message.receiver.id)

        sender = message.sender
        receiver = message.receiver
        
        if sender.role == "patient" and receiver.role in ['nurse', 'head nurse']:
            user = receiver
        elif sender.role == "patient" and receiver.role == "admin":
            user = sender
        else:
            user = message.sender if str(message.sender.id) != str(self.sender_id) else message.receiver


        user_profile = await self.get_profile(user)

        try:    
            
            await self.channel_layer.group_send(
                f"user_{receiver_user_id}",
                {
                    "type": "inbox_update",
                    "id": str(user.id),
                    "role": str(user.role).lower(),
                    "status": str(user.status).lower(),
                    "first_name": user.first_name,
                    "user_image": user_profile,
                    "message": message.content,
                    "message_status": message.status,
                    "read": message.read,
                    "chat_id": (
                        None if (
                            (sender.role == "patient" and receiver.role == "admin") or
                            (sender.role == "admin" and receiver.role == "patient")
                        ) else int(message.id)
                    ),
                    "sender_id": str(message.sender.id),
                    "receiver_id": str(message.receiver.id),
                    "time_sent": timezone.localtime(message.date_sent).strftime("%I:%M %p")
                }
            )
            
            print("[DEBUG] Successfully sent to inbox group")
        except Exception as e:
            print(f"[ERROR] Failed to send to inbox group: {e}")

    async def save_message(self, message_content, image_data=None):
        from app_chat.models import Message
        """Saves a new message to the database."""
        receiver_user = await self.get_user(self.receiver_id)
        sender_user = await self.get_user(self.sender_id)

        message = Message(
            sender=sender_user,
            receiver=receiver_user,
            content=message_content,    
            status='sent', #initially set status to 'sent',
            date_sent=timezone.now()
        )

        if image_data:
            try:

                size_in_bytes = get_base64_file_size(image_data)

                size_in_mb = size_in_bytes / (1024 * 1024)

                if size_in_mb >= 20:
                    await self.send_error_to_websocket("The image upload is too big")
                    return

                format, img_str = image_data.split(';base64,')
                ext = format.split('/')[-1] 
                message.image = ContentFile(base64.b64decode(img_str), name=f"{uuid.uuid4()}.{ext}")
            except Exception as e:
                print(f"[ERROR] Failed to decode image: {e}")

        #only save to DB if not patient-admin chat
        is_patient_admin_chat = (
            (receiver_user.role == "patient" and sender_user.role == "admin") or
            (receiver_user.role == "admin" and sender_user.role == "patient")
        )

        if not is_patient_admin_chat:
            await database_sync_to_async(message.save)()
            
        #return the message
        return message


    async def mark_message_as_read(self, message_id):
        from app_chat.models import Message
        try:
            #fetch the message from the database
            message = await database_sync_to_async(Message.objects.get)(id=message_id)

            #ensure the message is for the correct receiver
            if message.receiver.id == self.sender_id:
                
                #update the status and read 
                message.status = 'read'
                message.read = True

                #save the message obj
                await database_sync_to_async(message.save)()

        except Message.DoesNotExist:
            await self.send_error_to_websocket("Message not found")

    #helper function to get user from the database
    async def get_user(self, user_id) -> User:
        return await get_user_by_id(user_id)
    

    async def send_error_to_websocket(self, error_message):
        await self.send(text_data=json.dumps({
            "error": error_message
        }))

    @sync_to_async
    def get_profile(self, user):
        from app_authentication.models import Profile
        try:
            user_profile = Profile.objects.get(user=user)
            return user_profile.picture.url if user_profile and user_profile.picture else None
        except Profile.DoesNotExist:
            return None

        





