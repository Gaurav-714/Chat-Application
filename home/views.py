from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Subquery, OuterRef, Exists
from django.http import JsonResponse
from .models import ChatModel

User = get_user_model()


@login_required
def chat_view(request):
    query = request.GET.get('q', '').strip()
    username = request.GET.get('username', '').strip() 

    user_list = User.objects.values('username')

    # Subquery: Fetch the latest message per user chat
    latest_message_subquery = ChatModel.objects.filter(
        Q(sender=OuterRef('pk'), receiver=request.user) |
        Q(sender=request.user, receiver=OuterRef('pk'))
    ).order_by('-timestamp')

    # Fetch users with whom the authenticated user has chatted
    recent_chats = User.objects.filter(
        Exists(latest_message_subquery)
    ).annotate(
        latest_message_timestamp=Subquery(latest_message_subquery.values('timestamp')[:1]),
        latest_message_content=Subquery(latest_message_subquery.values('content')[:1])
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
        'user_list': user_list,      
        'recent_chats': recent_chats,
    }
    return render(request, 'index.html', context)


def login_view(request):
    return render(request, 'login.html')
