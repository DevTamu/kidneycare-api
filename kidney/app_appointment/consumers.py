import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from kidney.utils import get_user_by_id
from app_appointment.models import Appointment
from django.utils import timezone
from asgiref.sync import sync_to_async
import logging
from django.db.models import F, DateTimeField, ExpressionWrapper, Q
from datetime import timedelta

logger = logging.getLogger(__name__)

class AppointmentConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None

    async def connect(self):
        """Handles the WebSocket connection."""
        try:
            #user is already authenticated by middleware
            user = self.scope["user"]
            if not user:
                await self.close(code=4003)
                return
            
            #create chat room and join the chat room
            self.room_name = f"appointment_user_{user.id}"
            await self.channel_layer.group_add(self.room_name, self.channel_name)

            #accept the connection
            await self.accept()

        except Exception as e:
            await self.close(code=4003)
        
    async def disconnect(self, close_code):
        """Handles the WebSocket disconnection."""
        try:
            if hasattr(self, 'room_name') and self.room_name:
                await self.channel_layer.group_discard(self.room_name, self.channel_name)
        except Exception as e:
            print(f"[ERROR] Disconnect failed")

    async def receive(self, text_data):
        
        print(f"TEXT_DATA: {text_data}")

    
    # async def send_upcoming_appointment(self, appointment):

    #     await self.channel_layer.group_send(
    #         self.room_name,
    #         {}
    #     )


    async def upcoming_appointments(self, event):
        await self.send(text_data=json.dumps({
            "patient_id": event["patient_id"],
            "appointment_id": event["appointment_id"],
            "status": event["status"],
            "machine": event["machine"],
            "provider_name": event["provider_name"],
            "provider_image": event["provider_image"]
        }))


    




