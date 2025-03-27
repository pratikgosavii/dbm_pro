from django.contrib import admin
from .models import Lead, LeadSource, LeadStatus

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'source', 'status', 'assigned_to', 'created_at')
    list_filter = ('source', 'status', 'assigned_to', 'created_at')
    search_fields = ('name', 'email', 'phone', 'company')
    date_hierarchy = 'created_at'

@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(LeadStatus)
class LeadStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('order',)
