import json
import asyncio
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()


class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.user_group_name = 'user_status_updates'
            # Add the user to the group
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            await self.accept()

            # Broadcast the initial online status of all users
            await self.broadcast_online_users()

        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            # Broadcast a message that the user has gone offline
            await self.channel_layer.group_send(
                self.user_group_name,
                {
                    "type": "user_status_message",
                    "user_id": self.user.id,
                    "is_online": False,
                }
            )

            # Remove the user from the group
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def user_status_message(self, event):
        user_id = event['user_id']
        is_online = event['is_online']

        await self.send(text_data=json.dumps({
            'user_id': user_id,
            'is_online': is_online,
        }))

    @database_sync_to_async
    def get_online_users(self):
        """
        Synchronous function to query the database for online users.
        This must be run in a separate thread.
        """
        online_threshold = timezone.now() - timezone.timedelta(minutes=5)
        return list(User.objects.filter(last_seen__gte=online_threshold))

    async def broadcast_online_users(self):
        online_users = await self.get_online_users()

        for user in online_users:
            await self.channel_layer.group_send(
                self.user_group_name,
                {
                    "type": "user_status_message",
                    "user_id": user.id,
                    "is_online": True,
                }
            )
