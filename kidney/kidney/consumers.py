import json
from pprint import pprint
from app_chat.models import Message
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import database_sync_to_async, sync_to_async
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

@sync_to_async
def get_user_by_id(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_id = uuid.UUID(hex=self.scope["url_route"]["kwargs"]["receiver_id"])
        self.sender_id = self.scope['user'].id #logged in user (sender)
        print(self.receiver_id)
        pprint(self.receiver_id)
        # self.room_name = f"chat_{min(self.sender_id, self.receiver_id)}_{max(self.sender_id, self.receiver_id)}"  # Unique room for each pair
        pprint(f"connecting to room: {self.receiver_id}")
        self.room_group_name = f"chat_{self.receiver_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        pprint(f"connected to room: {self.room_group_name}")

    async def disconnect(self, close_code):
        # Leave room group
        pprint(f"Disconnecting from room: {self.room_group_name}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        pprint(f"disconnected from room: {self.room_group_name}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON data."}))
            return
        
        #update the database when the client reads the message by calling mark_message_as_read
        if data.get('type') == "message_read":
            message_id = data.get("message_id")
            if message_id:
                await self.mark_message_as_read(message_id)
            return
        
        if "message" not in data:
            await self.send(text_data=json.dumps({"error": "Message is required."}))
            return
        
        message_content = data["message"]

        message_obj = await self.save_message(message_content)

        await self.send_mesage_to_receiver(message_obj)

    async def send_mesage_to_receiver(self, message):
        """Send the message to the specific receiver."""

        await self.channel_layer.send(
            self.channel_name, #send to the receiver websocket
            {
                'type': 'chat_message',
                'message': message.content,
                'sender_id': message.sender.id,
                'message_id': message.id

            }
        )

    

    async def save_message(self, message_content):

        receiver_user = await get_user_by_id(str(self.receiver_id).replace("-", ""))
        sender_user = await get_user_by_id(self.sender_id)

        message = Message(
            sender=sender_user,
            receiver=receiver_user,
            content=message_content,
            status='sent' #initially sent status to 'sent'
        )
        #save the message obj
        await database_sync_to_async(message.save)()

        #return the message
        return message

    # Receive message from room group
    async def chat_message(self, event):

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": event["message"], #message content
            "sender_id": event["sender_id"], #sender id who to know which is the sender
            "message_id": event["message_id"] #message_id to identify specific message
        }))

    async def mark_message_as_read(self, message_id):
        try:
            #fetch the message from the database
            message = await database_sync_to_async(Message.objects.get)(id=message_id)

            if message.receiver.id == self.sender_id:

                #update the status as 'read' and read as 'True'
                message.status = 'read'
                message.read = True

                #save the message obj
                await database_sync_to_async(message.save)()

        except Message.DoesNotExist:
            await self.send(text_data=json.dumps({
                "error": "Message not found"
            }))