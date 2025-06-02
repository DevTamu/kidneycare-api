import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .utils import get_user_by_id
from app_authentication.models import User
from django.utils import timezone
from app_chat.models import Message
from django.db.models import Q



class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """Handles the WebSocket connection."""
        try:
            #user is already authenticated by middleware
            user = self.scope["user"]
            if not user:
                await self.close(code=4003)
                return

            self.receiver_id = self.scope["url_route"]["kwargs"]["room_name"]
            self.sender_id = str(user.id)
            
            self.room_group_name = f"chat_{min(self.receiver_id, self.sender_id)}_{max(self.receiver_id, self.sender_id)}"
            self.inbox_group_name = f"user_{self.sender_id}"

            #join both chat room and chat inbox group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.channel_layer.group_add(self.inbox_group_name, self.channel_name)
            await self.accept()

            user_receiver = await get_user_by_id(self.receiver_id)
            await self.send_message_introduction(user, user_receiver)
            
        except Exception as e:
            await self.close(code=4003)
        

    async def disconnect(self, close_code):
        """Handles the WebSocket disconnection."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.inbox_group_name, self.channel_name)

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
        
        message_content = data["message"]
        #if message not provided
        if not message_content:
            await self.send(text_data=json.dumps({"error": "Message is required."}))
            return
        
        #get the returned message from the save_message
        message_obj = await self.save_message(message_content)

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
                "message_id": str(message.id),
                "date_sent": message.created_at.isoformat(),
                "message_status": str(message.status).lower(),
            }
        )

    #receive message from room group
    async def chat_message(self, event): 
        """Handles broadcasting of the chat message to the WebSocket."""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": event["message"], #message content
            "sender_id": str(event["sender_id"]),
            "message_id": str(event["message_id"]),
            "date_sent": event["date_sent"],
            "message_status": event["message_status"],
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
        else:
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
            "type": "inbox_update",
            "provider_id": event["provider_id"],
            "role": event["role"],
            "status": event["status"],
            "first_name": event["first_name"],
            "user_image": event["user_image"],
            "last_message": {
                "message": event["message"],
                "status": event["status"],
                "read": event["is_read"],
                "chat_id": event["chat_id"],
                "sender_id": str(event["sender_id"]),
                "receiver_id": str(event["receiver_id"]),
                "time_sent": event["time_sent"]
            }
        }))

    async def send_message_to_inbox(self, message):

        receiver_user_id = str(message.receiver.id)
        provider = message.sender if str(message.sender.id) != str(self.sender_id) else message.receiver
        #send to inbox group
        if provider.role in ['nurse', 'head nurse']:
            await self.channel_layer.group_send(
                f"inbox_{receiver_user_id}",
                {
                    "type": "inbox_update",
                    "provider_id": str(provider.id),
                    "role": str(provider.role).lower(),
                    "status": str(provider.status).lower(),
                    "first_name": provider.first_name,
                    "user_image": provider.picture.url if hasattr(provider, "picture") else None,
                    "last_message": {
                        "message": message.content,
                        "message_status": message.status,
                        "read": str(message.read).lower(),
                        "chat_id": message.id,
                        "sender_id": str(message.sender.id),
                        "receiver_id": str(message.receiver.id),
                        "time_sent": timezone.localtime(message.date_sent).strftime("%I:%M %p")
                    }
                }
            )

    async def save_message(self, message_content):
        from app_chat.models import Message
        """Saves a new message to the database."""
        receiver_user = await self.get_user(self.receiver_id)
        sender_user = await self.get_user(self.sender_id)

        message = Message(
            sender=sender_user,
            receiver=receiver_user,
            content=message_content,    
            status='sent', #initially set status to 'sent',,
            date_sent=timezone.now()
        )

        #save the message obj
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


