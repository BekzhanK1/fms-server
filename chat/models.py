from django.db import models


class Room(models.Model):
    name = models.CharField(
        max_length=100, unique=True
    )  # e.g., "1-2" where user1_id < user2_id
    user1_id = models.IntegerField()
    user2_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.name} between {self.user1_id} and {self.user2_id}"


class Message(models.Model):
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="messages", blank=True, null=True
    )
    sender_id = models.IntegerField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender_id} in Room {self.room.name}"
