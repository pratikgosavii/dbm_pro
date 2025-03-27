from django.contrib import admin
from .models import Client, Project, Task

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0

class TaskInline(admin.TabularInline):
    model = Task
    extra = 0

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone')
    search_fields = ('name', 'contact_person', 'email')
    inlines = [ProjectInline]

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'status', 'start_date', 'end_date', 'budget')
    list_filter = ('status', 'start_date')
    search_fields = ('name', 'client__name', 'description')
    inlines = [TaskInline]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'priority', 'due_date')
    list_filter = ('status', 'priority', 'due_date')
    search_fields = ('title', 'description', 'project__name', 'assigned_to__username')
