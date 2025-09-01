# Employee_System/consumers.py
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User


class OnlineStatusConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Access the authenticated user from the WebSocket scope
        user = self.scope["user"]

        if user.is_authenticated:
            # Set the user's status to online in the database
            # You should have a custom user model or a profile model for this
            # e.g., user.profile.is_online = True; await user.profile.asave()

            # Add the user's ID to the channel group
            self.user_group_name = f'user_{user.id}'
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )

            # Send a broadcast message to all clients to update the user's status
            await self.channel_layer.group_send(
                'online_status_group',
                {
                    'type': 'status_update',
                    'user_id': user.id,
                    'is_online': True,
                }
            )
            await self.accept()

    async def disconnect(self, close_code):
        user = self.scope["user"]

        if user.is_authenticated:
            # Set the user's status to offline in the database
            # e.g., user.profile.is_online = False; await user.profile.asave()

            # Remove the user from the channel group
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

            # Send a broadcast message to all clients to update the user's status
            await self.channel_layer.group_send(
                'online_status_group',
                {
                    'type': 'status_update',
                    'user_id': user.id,
                    'is_online': False,
                }
            )

    async def status_update(self, event):
        # This function is called when a message is sent to the 'online_status_group'
        await self.send_json(event)