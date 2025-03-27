from django.contrib import admin
from .models import ChatGroup, Message

@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    filter_horizontal = ('members',)
    readonly_fields = ('created_at', 'updated_at')
    
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'get_receiver', 'get_group', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read')
    search_fields = ('content', 'sender__username', 'receiver__username', 'group__name')
    readonly_fields = ('timestamp',)
    
    def get_receiver(self, obj):
        return obj.receiver.username if obj.receiver else '-'
    get_receiver.short_description = 'Receiver'
    
    def get_group(self, obj):
        return obj.group.name if obj.group else '-'
    get_group.short_description = 'Group'
