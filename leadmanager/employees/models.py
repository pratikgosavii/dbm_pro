from django.db import models
from django.contrib.auth.models import User
import datetime


class Department(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    joining_date = models.DateField()
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=15, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email


class TimeRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='time_records')
    date = models.DateField()
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.date}"
    
    @property
    def hours_worked(self):
        if self.time_in and self.time_out:
            # Convert time to datetime for calculation
            time_in_dt = datetime.datetime.combine(datetime.date.today(), self.time_in)
            time_out_dt = datetime.datetime.combine(datetime.date.today(), self.time_out)
            
            # If time_out is earlier than time_in, assume it's the next day
            if time_out_dt < time_in_dt:
                time_out_dt += datetime.timedelta(days=1)
            
            # Calculate difference in hours
            diff = time_out_dt - time_in_dt
            return round(diff.total_seconds() / 3600, 2)
        return None
    
    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date', '-time_in']
