from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Room, Message

User = get_user_model()  # Use the custom User model if applicable


class ListChatRoomsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Get rooms where the user is either user1 or user2
        rooms = Room.objects.filter(user1_id=user.id)
        rooms2 = Room.objects.filter(user2_id=user.id)
        rooms = list(rooms) + list(rooms2)

        response = []
        for room in rooms:
            # Get the last message in the room
            last_message = (
                Message.objects.filter(room=room).order_by("-timestamp").first()
            )

            # Determine the companion's ID
            companion_id = room.user2_id if room.user1_id == user.id else room.user1_id
            companion = User.objects.get(id=companion_id)

            # Construct response for each room
            response.append(
                {
                    "room_name": room.name,
                    "companion": {
                        "id": companion.id,
                        "full_name": f"{companion.first_name} {companion.last_name}",
                        "email": companion.email,
                    },
                    "last_message": {
                        "who": (
                            "me" if last_message.sender_id == user.id else "companion"
                        ),
                        "message": last_message.message,
                        "timestamp": last_message.timestamp,
                    },
                }
            )

        return Response(response)


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_name):
        user = request.user
        try:
            # Retrieve the room by name
            room = Room.objects.get(name=room_name)

            # Determine the companion ID
            if room.user1_id == user.id:
                companion_id = room.user2_id
            elif room.user2_id == user.id:
                companion_id = room.user1_id
            else:
                return Response(
                    {"error": "You are not a participant in this room"}, status=403
                )

            # Retrieve companion details
            try:
                companion = User.objects.get(id=companion_id)
            except User.DoesNotExist:
                return Response({"error": "Companion does not exist"}, status=404)

            # Retrieve chat messages
            messages = room.messages.order_by("timestamp").values(
                "sender_id", "message", "timestamp"
            )
            processed_messages = [
                {
                    "sender_id": msg["sender_id"],
                    "message": msg["message"],
                    "timestamp": msg["timestamp"],
                    "who": "me" if msg["sender_id"] == user.id else "companion",
                }
                for msg in messages
            ]

            # Prepare the response
            response = {
                "companion": {
                    "id": companion.id,
                    "full_name": companion.first_name + " " + companion.last_name,
                    "email": companion.email,
                },
                "messages": list(processed_messages),
            }
            return Response(response)

        except Room.DoesNotExist:
            return Response({"error": "Room does not exist"}, status=404)
