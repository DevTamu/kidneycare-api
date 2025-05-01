import json
from pprint import pprint

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        pprint(f"connecting to room: {self.room_name}")
        self.room_group_name = f"chat_{self.room_name}"

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

        if "message" not in data:
            await self.send(text_data=json.dumps({"error": "Message is required."}))
            return

        message = data["message"]

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
