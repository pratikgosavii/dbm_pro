from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('late', 'Late'),
    )
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    punch_in_time = models.TimeField(blank=True, null=True)
    punch_out_time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date', 'employee']
    
    def __str__(self):
        return f"{self.employee.username} - {self.date} - {self.get_status_display()}"
    
    @property
    def hours_worked(self):
        if self.punch_in_time and self.punch_out_time:
            punch_in_dt = datetime.datetime.combine(self.date, self.punch_in_time)
            punch_out_dt = datetime.datetime.combine(self.date, self.punch_out_time)
            
            if punch_out_dt < punch_in_dt:
                # If punch out is next day
                punch_out_dt += datetime.timedelta(days=1)
            
            duration = punch_out_dt - punch_in_dt
            return round(duration.total_seconds() / 3600, 2)
        return 0

class Salary(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    
    MONTH_CHOICES = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salaries')
    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_salaries')
    
    class Meta:
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month', 'employee']
    
    def __str__(self):
        return f"{self.employee.username} - {self.get_month_display()} {self.year}"
    
    @property
    def net_amount(self):
        return self.amount + self.bonus - self.deduction
