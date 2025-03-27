from django.contrib import admin
from .models import Lead, LeadSource, LeadStatus

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'source', 'status', 'assigned_to', 'created_at')
    list_filter = ('source', 'status', 'assigned_to', 'created_at')
    search_fields = ('name', 'email', 'phone')
    date_hierarchy = 'created_at'

@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(LeadStatus)
class LeadStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_converted')
