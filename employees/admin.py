from django.contrib import admin
from .models import Attendance, Salary

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'punch_in_time', 'punch_out_time', 'status')
    list_filter = ('date', 'status', 'employee')
    search_fields = ('employee__username', 'employee__first_name', 'employee__last_name')
    date_hierarchy = 'date'

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'year', 'amount', 'status', 'payment_date')
    list_filter = ('month', 'year', 'status')
    search_fields = ('employee__username', 'employee__first_name', 'employee__last_name')
