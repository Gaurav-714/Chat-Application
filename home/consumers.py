from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import ChatModel

User = get_user_model()

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_name = f"room_{self.user.username}" 
        self.channel_layer = get_channel_layer()

        if not self.user.is_authenticated:
            await self.close()
            return
        
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

        

        print(f"✅ {self.user.username} connected to WebSocket.")

    @database_sync_to_async
    def get_chat_history(self):
        """ Fetch all messages where the user is sender or receiver and serialize datetime. """
        chats = ChatModel.objects.filter(
            Q(sender=self.user) | Q(receiver=self.user)
        ).order_by('timestamp').values('sender__username', 'receiver__username', 'content', 'timestamp')

        # Convert queryset to a list and format datetime objects
        chat_list = list(chats)
        for chat in chat_list:
            if chat["timestamp"]:  
                chat["timestamp"] = chat["timestamp"].isoformat()  # Converts datetime to string

        return chat_list

    async def receive_json(self, content, **kwargs):
        receiver_username = content.get('receiver') 
        message = content.get('message') 
        
        if not receiver_username or not message:
            return
        
        try:
            # Fetch user's chat history asynchronously
            chat_history = await self.get_chat_history()
        
            # Send chat history to the user
            await self.send_json({
                "type": "chat.history",
                "messages": chat_history
            })
            
            receiver = await database_sync_to_async(User.objects.get)(username=receiver_username)
            chat_instance = await database_sync_to_async(ChatModel.objects.create)(
                content=message, sender=self.user, receiver=receiver
            )

            # Convert timestamp to ISO format before sending
            timestamp_str = chat_instance.timestamp.isoformat()

            await self.channel_layer.group_send(
                f"room_{receiver_username}", {
                    'type': 'chat.message',
                    'message': message,
                    'sender': self.user.username,
                    'timestamp': timestamp_str
                }
            )

        except User.DoesNotExist:
            print(f"❌ User '{receiver_username}' does not exist.")

    async def chat_message(self, event):
        await self.send_json({
            "message": event['message'],
            "sender": event['sender'],
            "timestamp": event.get('timestamp', '')
        })

    async def disconnect(self, close_code):
        print(f"❌ {self.user.username} disconnected from WebSocket.")
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
