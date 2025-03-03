from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime

User = get_user_model()

class ChatModel(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        display_timestamp = localtime(self.timestamp).strftime("%I:%M %p, %d %b %Y")
        return f"{self.sender} -> {self.receiver}: {self.content[:30]} @ {display_timestamp}"