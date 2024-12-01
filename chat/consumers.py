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
        # Authenticate the user
        self.scope["user"] = await self.get_user_from_token()
        if not self.scope["user"]:
            await self.close()  # Close connection if the user is not authenticated
            return

        original_room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_name = await self.format_room_name(original_room_name)

        if not self.room_name:
            await self.close()  # Close connection if the room is invalid
            return

        self.room_group_name = f"chat_{self.room_name}"

        if not await self.is_valid_room():
            await self.close()  # Close connection if the room is invalid
            return

        # Debug: Log user joining the room
        print(f"User {self.scope['user'].email} is joining room { self.room_group_name}")

        # Add the client to the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Debug: Log user disconnecting
        print( f"User {self.scope['user'].email} is disconnecting from { self.room_group_name}" )

        # Remove the client from the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender = self.scope["user"]

        # Debug: Log received message
        print(f"Received message from {sender.email}: {message}")


        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender.email,
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]

        # Debug: Log the sender and receiver
        print(f"Sender: {sender}")
        print(f"Current User (receiver): {self.scope['user'].email}")
        await self.save_message(self.room_name, sender, message)

        # Send the message to the WebSocket client only if the current user is NOT the sender
        print(f"Sending message to: {self.scope['user'].email}")
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
        token = query_params.get("token", [None])[0]

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
    def format_room_name(self, room_name):
        try:
            user_ids = room_name.split("-")
            if len(user_ids) != 2:
                return None

            user1_id, user2_id = map(int, user_ids)
            user1_id, user2_id = sorted([user1_id, user2_id])
            return f"{user1_id}-{user2_id}"
        except (ValueError, TypeError):
            return None

    @database_sync_to_async
    def is_valid_room(self):
        try:
            user_ids = self.room_name.split("-")
            if len(user_ids) != 2:
                return False

            user1_id, user2_id = map(int, user_ids)

            user1_exists = User.objects.filter(id=user1_id).exists()
            user2_exists = User.objects.filter(id=user2_id).exists()

            if not user1_exists or not user2_exists:
                return False

            if self.scope["user"].id not in [user1_id, user2_id]:
                return False

            return True
        except (ValueError, TypeError):
            return False
    
    @database_sync_to_async
    def save_message(self, room_name, sender_email, message_content):
        try:
            # Find the Room by room_name
            room = Room.objects.get(name=room_name)
            
            # Find the User by sender_email
            sender = User.objects.get(email=sender_email)

            # Save the message
            Message.objects.create(
                room=room,
                sender_id=sender.pk,
                message=message_content,
            )
        except Room.DoesNotExist:
            print(f"Room with name {room_name} does not exist.")
        except User.DoesNotExist:
            print(f"User with email {sender_email} does not exist.")