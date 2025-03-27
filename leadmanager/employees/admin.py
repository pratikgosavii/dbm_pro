from django.contrib import admin
from .models import Employee, TimeRecord, Department


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'position', 'joining_date')
    list_filter = ('department', 'joining_date')
    search_fields = ('user__username', 'user__email', 'position')


@admin.register(TimeRecord)
class TimeRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'time_in', 'time_out', 'hours_worked')
    list_filter = ('date', 'employee')
    search_fields = ('employee__user__username',)
    date_hierarchy = 'date'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
