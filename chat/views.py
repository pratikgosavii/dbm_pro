from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q
from .models import ChatGroup, Message
from .forms import ChatGroupForm, MessageForm, DirectMessageForm

@login_required
def inbox(request):
    """View for user's message inbox"""
    # Get user's chat groups
    groups = request.user.chat_groups.all()
    
    # Get direct messages (both sent and received)
    direct_messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        group__isnull=True
    ).order_by('timestamp')
    
    # Process conversations for template
    conversation_users = set()
    for msg in direct_messages:
        if msg.sender == request.user:
            conversation_users.add(msg.receiver)
        else:
            conversation_users.add(msg.sender)
    
    # Prepare conversation data
    recent_conversations = []
    for user in conversation_users:
        # Get the most recent message in this conversation
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(sender=user) & Q(receiver=request.user)),
            group__isnull=True
        ).order_by('-timestamp').first()
        
        # Count unread messages
        unread_count = Message.objects.filter(
            sender=user,
            receiver=request.user,
            is_read=False,
            group__isnull=True
        ).count()
        
        recent_conversations.append({
            'user': user,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    # Sort conversations by most recent message timestamp
    recent_conversations.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else None, reverse=True)
    
    # Process groups for the template
    group_data = []
    for group in groups:
        # Get the most recent message in this group
        last_message = Message.objects.filter(group=group).order_by('-timestamp').first()
        
        # Count unread messages (for now a simple count of messages not sent by the user)
        unread_count = Message.objects.filter(
            group=group,
            sender__isnull=False,  # Ensure we're not counting system messages
            is_read=False
        ).exclude(sender=request.user).count()  # Don't count user's own messages
        
        group_data.append({
            'id': group.id,
            'name': group.name,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    # Sort groups by most recent message timestamp
    group_data.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else None, reverse=True)
    
    context = {
        'recent_conversations': recent_conversations,
        'groups': group_data,
    }
    
    return render(request, 'chat/inbox.html', context)

@login_required
def create_group(request):
    """View to create a new chat group"""
    if request.method == 'POST':
        form = ChatGroupForm(request.POST, user=request.user)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            # Add the current user and selected members
            group.members.add(request.user)
            group.members.add(*form.cleaned_data['members'])
            messages.success(request, f"Chat group '{group.name}' created successfully!")
            return redirect('chat:group_chat', group_id=group.id)
    else:
        form = ChatGroupForm(user=request.user)
    
    return render(request, 'chat/create_group.html', {'form': form})

@login_required
def edit_group(request, group_id):
    """View to edit a chat group"""
    group = get_object_or_404(ChatGroup, id=group_id)
    
    # Check if user is the creator of the group
    if group.created_by != request.user:
        messages.error(request, "You don't have permission to edit this group.")
        return redirect('chat:inbox')
    
    if request.method == 'POST':
        form = ChatGroupForm(request.POST, instance=group, user=request.user)
        if form.is_valid():
            updated_group = form.save()
            # Make sure the current user is still a member
            updated_group.members.add(request.user)
            messages.success(request, f"Chat group '{updated_group.name}' updated successfully!")
            return redirect('chat:group_chat', group_id=group.id)
    else:
        form = ChatGroupForm(instance=group, user=request.user)
    
    return render(request, 'chat/edit_group.html', {'form': form, 'group': group})

@login_required
def delete_group(request, group_id):
    """View to delete a chat group"""
    group = get_object_or_404(ChatGroup, id=group_id)
    
    # Check if user is the creator of the group
    if group.created_by != request.user:
        messages.error(request, "You don't have permission to delete this group.")
        return redirect('chat:inbox')
    
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f"Chat group '{group_name}' deleted successfully!")
        return redirect('chat:inbox')
    
    return render(request, 'chat/delete_group.html', {'group': group})

@login_required
def group_chat(request, group_id):
    """View for chat within a group"""
    group = get_object_or_404(ChatGroup, id=group_id)
    
    # Check if user is a member of the group
    if request.user not in group.members.all():
        messages.error(request, "You are not a member of this chat group.")
        return redirect('chat:inbox')
    
    # Get group messages
    group_messages = group.messages.all().order_by('timestamp')
    
    # Mark messages as read
    unread_messages = group_messages.filter(is_read=False).exclude(sender=request.user)
    for msg in unread_messages:
        msg.is_read = True
        msg.save()
    
    # Form for sending a new message
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.group = group
            message.save()
            return redirect('chat:group_chat', group_id=group.id)
    else:
        form = MessageForm()
    
    context = {
        'group': group,
        'group_messages': group_messages,
        'form': form,
    }
    return render(request, 'chat/group_chat.html', context)

@login_required
def direct_message(request, user_id):
    """View for direct messaging with another user"""
    receiver = get_object_or_404(User, id=user_id)
    
    # Get conversation history
    conversation = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) |
        (Q(sender=receiver) & Q(receiver=request.user)),
        group__isnull=True
    ).order_by('timestamp')
    
    # Mark messages from receiver as read
    unread_messages = conversation.filter(sender=receiver, is_read=False)
    for msg in unread_messages:
        msg.is_read = True
        msg.save()
    
    # Form for sending a new message
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            return redirect('chat:direct_message', user_id=receiver.id)
    else:
        form = MessageForm()
    
    context = {
        'receiver': receiver,
        'conversation': conversation,
        'form': form,
    }
    return render(request, 'chat/direct_message.html', context)

@login_required
def start_conversation(request):
    """View to start a new direct message conversation"""
    if request.method == 'POST':
        form = DirectMessageForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = form.cleaned_data['receiver']
            message.save()
            return redirect('chat:direct_message', user_id=message.receiver.id)
    else:
        form = DirectMessageForm(user=request.user)
    
    return render(request, 'chat/start_conversation.html', {'form': form})
