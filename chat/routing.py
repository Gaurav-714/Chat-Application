from django.urls import re_path
from chat.consumers import ChatConsumer, ChatPreviewConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/$", ChatConsumer.as_asgi()),
    re_path(r"ws/chat-preview/$", ChatPreviewConsumer.as_asgi()),
]