from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ChatGroup(models.Model):
    """Model for group chats"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(User, related_name='chat_groups')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_chat_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class Message(models.Model):
    """Model for chat messages"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    content = models.TextField()
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    document = models.FileField(upload_to='chat_documents/', null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        if self.group:
            return f"Group message in {self.group.name} by {self.sender.username}"
        return f"Message from {self.sender.username} to {self.receiver.username}"
    
    class Meta:
        ordering = ['timestamp']
        
    def is_direct_message(self):
        """Check if message is a direct message or group message"""
        return self.receiver is not None
