from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Max, Q, Subquery, OuterRef
from django.http import JsonResponse
from .models import ChatModel

User = get_user_model()

@login_required
def chat_view(request):
    query = request.GET.get('q', '').strip()  # Search query for users
    username = request.GET.get('username', '').strip()  # Username for chat history

    # Fetch all registered users for searching
    user_list = User.objects.values('username')

    # Fetch recent chats with content and timestamp of the lastest message
    latest_message_subquery = ChatModel.objects.filter(
        Q(sender=OuterRef('pk'), receiver=request.user) | 
        Q(sender=request.user, receiver=OuterRef('pk'))
    ).order_by('-timestamp').values('content')[:1]

    recent_chats = User.objects.filter(
        Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
    ).annotate(
        latest_message_timestamp=Max('sent_messages__timestamp', 'received_messages__timestamp'),
        latest_message_content=Subquery(latest_message_subquery)
    ).order_by('-latest_message_timestamp')

    # Handle AJAX requests separately
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle search functionality
        if query:
            filtered_users = user_list.filter(Q(username__icontains=query))
            return JsonResponse({'user_list': list(filtered_users)})

        # Handle fetching chat history
        if username:
            chat_history = ChatModel.objects.filter(
                Q(sender__username=username, receiver=request.user) |
                Q(sender=request.user, receiver__username=username)
            ).order_by('timestamp')

            # Serialize chat history properly
            chat_data = list(chat_history.values('sender__username', 'receiver__username', 'content', 'timestamp'))
            return JsonResponse({'chat_history': chat_data})

    context = {
        'user_list': user_list,       # Full user list for searching
        'recent_chats': recent_chats, # Users with whom the user has chatted
    }
    return render(request, 'index.html', context)


def login_view(request):
    return render(request, 'login.html')