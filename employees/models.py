from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from django.db.models import Sum, Count
from calendar import monthrange

class LeaveApplication(models.Model):
    """Model for leave applications"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    )
    
    LEAVE_TYPE_CHOICES = (
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('annual', 'Annual Leave'),
        ('paternity', 'Paternity Leave'),
        ('maternity', 'Maternity Leave'),
        ('bereavement', 'Bereavement Leave'),
        ('unpaid', 'Unpaid Leave'),
        ('other', 'Other'),
    )
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_applications')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    response_date = models.DateTimeField(null=True, blank=True)
    admin_remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-applied_on']
    
    def __str__(self):
        return f"{self.employee.username} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"
    
    @property
    def duration(self):
        """Calculate duration of leave in days"""
        delta = self.end_date - self.start_date
        return delta.days + 1  # inclusive of both start and end date
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def is_past_leave(self):
        return self.end_date < timezone.now().date()
    
    def save(self, *args, **kwargs):
        # If status is changed to approved or declined, set response_date
        if self.pk:
            old_instance = LeaveApplication.objects.get(pk=self.pk)
            if old_instance.status != self.status and self.status in ['approved', 'declined']:
                self.response_date = timezone.now()
        super().save(*args, **kwargs)
        
        # If approved, create attendance records for the leave period
        if self.status == 'approved':
            current_date = self.start_date
            while current_date <= self.end_date:
                # Skip weekends if needed
                # if current_date.weekday() < 5:  # Monday to Friday
                Attendance.objects.update_or_create(
                    employee=self.employee,
                    date=current_date,
                    defaults={'status': 'absent', 'notes': f"On {self.get_leave_type_display()}"}
                )
                current_date += datetime.timedelta(days=1)

class EmployeeTask(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    completed_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'due_date', 'status']
    
    def __str__(self):
        return self.title
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    @property
    def is_overdue(self):
        if self.due_date and not self.is_completed and self.due_date < timezone.now().date():
            return True
        return False
    
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
        """Calculate hours worked based on punch in and punch out times"""
        if self.punch_in_time and self.punch_out_time:
            punch_in_dt = datetime.datetime.combine(self.date, self.punch_in_time)
            punch_out_dt = datetime.datetime.combine(self.date, self.punch_out_time)
            
            # If punch out is earlier than punch in (crossed midnight), add a day
            if punch_out_dt < punch_in_dt:
                punch_out_dt += datetime.timedelta(days=1)
                
            # Calculate the time difference in hours
            duration = punch_out_dt - punch_in_dt
            return round(duration.total_seconds() / 3600, 2)
        return 0.0

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
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monthly base salary")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Calculated salary after attendance adjustment")
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    days_present = models.IntegerField(default=0, help_text="Number of days present in the month")
    working_days = models.IntegerField(default=0, help_text="Total working days in the month")
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
    
    @property
    def attendance_percentage(self):
        """Calculate attendance percentage"""
        if self.working_days == 0:
            return 0
        return (self.days_present / self.working_days) * 100
    
    def calculate_salary(self):
        """Calculate salary based on attendance"""
        # Get the number of days in the month
        num_days = monthrange(self.year, self.month)[1]
        
        # Set working days (default to all days in month, can be customized)
        self.working_days = num_days
        
        # Count attendance records for this employee in this month/year
        start_date = datetime.date(self.year, self.month, 1)
        end_date = datetime.date(self.year, self.month, num_days)
        
        # Count days marked as present
        present_days = Attendance.objects.filter(
            employee=self.employee,
            date__range=[start_date, end_date],
            status='present'
        ).count()
        
        # Count half days (each counts as 0.5)
        half_days = Attendance.objects.filter(
            employee=self.employee,
            date__range=[start_date, end_date],
            status='half_day'
        ).count()
        
        # Calculate total days present
        self.days_present = present_days + (half_days * 0.5)
        
        # Calculate salary based on days present
        daily_rate = self.base_salary / self.working_days
        self.amount = round(daily_rate * self.days_present, 2)
        
        return self.amount
    
    def save(self, *args, **kwargs):
        # If this is a new salary record or base_salary changed
        if not self.pk or (self.pk and Salary.objects.get(pk=self.pk).base_salary != self.base_salary):
            # Only override amount if explicitly calculating
            if kwargs.pop('calculate', False):
                self.calculate_salary()
                
        super().save(*args, **kwargs)
