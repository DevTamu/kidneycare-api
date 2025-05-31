import json
from pprint import pprint
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .utils import get_user_by_id
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from app_authentication.models import User

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # pprint(f"connecting to room: {self.room_name}")
        self.room_group_name = f"chat_{self.room_name}"


        user = self.scope.get("user")
        if user is None or user.is_anonymous:
            await self.close(code=4002)
            return

        self.sender_id = str(user.id).replace("-", "")
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{min(self.room_name, self.sender_id)}_{max(self.room_name, self.sender_id)}"
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        # pprint(f"connected to room: {self.room_group_name}")

    async def disconnect(self, close_code):
        # Leave room group
        # pprint(f"Disconnecting from room: {self.room_group_name}")

        user_receiver = await get_user_by_id(self.room_name)
        await self.send_message_introduction(user, user_receiver)
        

    async def disconnect(self, close_code):
        """Handles the WebSocket disconnection."""
        pprint(f"Disconnecting from room: {self.room_group_name}")    
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # pprint(f"disconnected from room: {self.room_group_name}")

    async def receive(self, text_data):
        
        #re-validate token on every message
        try:
            token = AccessToken(self.token)
            self.sender_id = str(token["user_id"]).replace("-", "")
        except TokenError:
            await self.send_error_to_websocket("Invalid or expired token. Please log in again.")
            await self.close(code=4002)
            return

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

        await self.send_message_to_receiver(message_obj)

    async def send_message_to_receiver(self, message):
        """Send the saved message to the receiver."""
        await self.channel_layer.group_send(
            self.room_group_name, #send to the receiver websocket
            {
                'type': 'chat_message',  #this will call the 'chat_message' method on the receiver's side
                'message': message.content,
                'sender_id': message.sender.id,
                'message_id': message.id,
                'date_sent': message.created_at
            }
        )

    async def send_message_introduction(self, sender, receiver):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message_introduction',
                'message': f"Hi {sender.first_name.capitalize()} {receiver.last_name.capitalize()}, this is {receiver.first_name.capitalize()} from Boho Renal Care. I'd be happy to assist you",
                "sender_id": sender.id,
                "receiver_id": receiver.id  
            }
        )

    async def chat_message_introduction(self, event):
        await self.send(text_data=json.dumps({
            'introduction_message': event['message'],
            'sender': str(event['sender_id']),
            'receiver': str(event['receiver_id']),
        }))

    async def save_message(self, message_content):
        from app_chat.models import Message
        """Saves a new message to the database."""
        receiver_user = await self.get_user(self.room_name)
        sender_user = await self.get_user(self.sender_id)

        message = Message(
            sender=sender_user,
            receiver=receiver_user,
            content=message_content,    
            status='sent' #initially set status to 'sent',
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

    # Receive message from room group
    async def chat_message(self, event):
        
        """Handles broadcasting of the chat message to the WebSocket."""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": event["message"], #message content
            "sender_id": str(event["sender_id"]),
            "message_id": str(event["message_id"])
        }))

    #helper function to get user from the database
    async def get_user(self, user_id) -> User:
        return await get_user_by_id(user_id)
    

    async def send_error_to_websocket(self, error_message):
        await self.send(text_data=json.dumps({
            "error": error_message
        }))k