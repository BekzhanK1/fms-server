from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
import json

from chat.models import Message, Room

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Extract and validate the JWT token
        self.scope["user"] = await self.get_user_from_token()

        if not self.scope["user"]:
            await self.close()  # Close connection if the user is not authenticated
            return

        # Original room name from the WebSocket URL
        original_room_name = self.scope["url_route"]["kwargs"]["room_name"]

        # Ensure room name is in the correct format
        self.room_name = await self.format_room_name(original_room_name)

        if not self.room_name:
            await self.close()  # Close connection if the room is invalid
            return

        self.room_group_name = f"chat_{self.room_name}"

        # Validate room and users
        if not await self.is_valid_room():
            await self.close()  # Close connection if the room is invalid
            return

        # Join the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

    @database_sync_to_async
    def format_room_name(self, room_name):
        """
        Ensures the room name is in the correct format: 'user1_id-user2_id' where user1_id < user2_id.
        """
        try:
            user_ids = room_name.split("-")
            if len(user_ids) != 2:
                return None

            user1_id, user2_id = map(int, user_ids)

            # Sort the IDs to ensure user1_id < user2_id
            user1_id, user2_id = sorted([user1_id, user2_id])

            # Return the correctly formatted room name
            return f"{user1_id}-{user2_id}"
        except (ValueError, TypeError):
            # Handle invalid room name format
            return None

    @database_sync_to_async
    def is_valid_room(self):
        """
        Validates the room format and ensures both users exist and the connecting user is one of them.
        """
        try:
            user_ids = self.room_name.split("-")
            if len(user_ids) != 2:
                return False

            user1_id, user2_id = map(int, user_ids)

            # Ensure both users exist
            user1_exists = User.objects.filter(id=user1_id).exists()
            user2_exists = User.objects.filter(id=user2_id).exists()

            if not user1_exists or not user2_exists:
                return False

            # Ensure the connecting user is one of the participants
            if self.scope["user"].id not in [user1_id, user2_id]:
                return False

            return True
        except (ValueError, TypeError):
            # Handle invalid room name format
            return False

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data):
        # Extract the message and sender (authenticated user)
        data = json.loads(text_data)
        message = data["message"]
        sender = self.scope["user"]

        # Save the message to the database
        await self.save_message(sender.id, message)

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender.email,  # Include the sender's username
            },
        )

    async def chat_message(self, event):
        # Receive a message broadcast from the group
        message = event["message"]
        sender = event["sender"]

        # Send the message back to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "sender": sender,
                }
            )
        )

    @database_sync_to_async
    def get_user_from_token(self):
        query_params = parse_qs(self.scope["query_string"].decode())
        token = query_params.get("token", [None])[0]  # Extract token from query string

        if not token:
            return None

        try:
            # Validate the token
            UntypedToken(token)
            payload = UntypedToken(token).payload
            user_id = payload.get("user_id")
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None

    @database_sync_to_async
    def save_message(self, sender_id, message):
        # Save the message to the database
        room = Room.objects.get(name=self.room_name)
        Message.objects.create(room=room, sender_id=sender_id, message=message)
