from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime
from django.db.models import Q
from .models import ChatModel

User = get_user_model()

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.room_name = f"room_{self.user.username}"
        self.channel_layer = get_channel_layer()
        
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        
        print(f"✅ {self.user.username} connected to WebSocket.")

        # Send chat history on connect
        chat_history = await self.get_chat_history()
        await self.send_json({
            "type": "chat.history",
            "messages": chat_history
        })

    @database_sync_to_async
    def get_chat_history(self):
        """ Fetch all messages where the user is sender or receiver and serialize datetime. """
        chats = ChatModel.objects.filter(
            Q(sender=self.user) | Q(receiver=self.user)
        ).order_by('timestamp').values('sender__username', 'receiver__username', 'content', 'timestamp')

        chat_list = list(chats)
        for chat in chat_list:
            if chat["timestamp"]:  
                chat["timestamp"] = chat["timestamp"].isoformat()  # Convert datetime to string

        return chat_list

    async def receive_json(self, content, **kwargs):
      
        receiver_username = content.get("receiver") 
        message = content.get("message") 
        
        if not receiver_username or not message:
            return
        
        try:
            receiver = await database_sync_to_async(User.objects.get)(username=receiver_username)
            
            chat_instance = await database_sync_to_async(ChatModel.objects.create)(
                content=message, sender=self.user, receiver=receiver
            )
            timestamp_str = localtime(chat_instance.timestamp).strftime("%I:%M %p, %d %b %Y")

            # Send message to receiver's room
            await self.channel_layer.group_send(
                f"room_{receiver_username}",
                {
                    "type": "chat.message",
                    "message": message,
                    "sender": self.user.username,
                    "timestamp": timestamp_str
                }
            )

            # Send the latest message confirmation
            await self.send_json({
                "type": "chat.sent",
                "message": message,
                "receiver": receiver_username,
                "timestamp": timestamp_str
            })

        except User.DoesNotExist:
            print(f"❌ User '{receiver_username}' does not exist.")
            await self.send_json({
                "type": "error",
                "message": "Receiver does not exist."
            })

    async def chat_message(self, event):
        """ Send the received message to the WebSocket client """
        await self.send_json({
            "type": "chat.message",
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event.get("timestamp", "")
        })

    async def chat_preview(self, event):
        pass  

    async def disconnect(self, close_code):
        if hasattr(self, "user") and self.user.is_authenticated:
            print(f"❌ {self.user.username} disconnected from WebSocket.")
            await self.channel_layer.group_discard(self.room_name, self.channel_name)


class ChatPreviewConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.room_name = f"room_{self.user.username}"
        self.channel_layer = get_channel_layer()
        
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        
        print(f"✅ {self.user.username} connected to Chat Preview WebSocket.")

    async def receive_json(self, content, **kwargs):
        message_preview = content.get("message_preview")
        receiver_username = content.get("receiver")

        print(f'### message_preview for {receiver_username}: ', message_preview)  

        if not receiver_username or not message_preview:
            return

        await self.channel_layer.group_send(
            f"room_{receiver_username}", {
                "type": "chat.preview", 
                "message": message_preview,
                "sender": self.user.username,
            } 
        )

    async def chat_preview(self, event):       
        await self.send_json({
            "type": "chat.preview",
            "message": event["message"],
            "sender": event["sender"],
        })

    async def chat_message(self, event):
        pass

    async def disconnect(self, close_code):
        if hasattr(self, "user") and self.user.is_authenticated:
            print(f"❌ {self.user.username} disconnected from Chat Preview WebSocket.")
            await self.channel_layer.group_discard(self.room_name, self.channel_name)
