from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from projects.models import Project

class Task(models.Model):
    """Task model for assigning work to employees"""
    
    # Task priority choices
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'
    
    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
        (URGENT, 'Urgent'),
    ]
    
    # Task status choices
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    REVIEW = 'review'
    DONE = 'done'
    
    STATUS_CHOICES = [
        (TODO, 'To Do'),
        (IN_PROGRESS, 'In Progress'),
        (REVIEW, 'Under Review'),
        (DONE, 'Done'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=MEDIUM)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=TODO)
    due_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['due_date', 'priority']
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status != self.DONE
    
    @property
    def is_done(self):
        return self.status == self.DONE

class Attendance(models.Model):
    """Model for tracking employee attendance"""
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.employee.username} - {self.date}"
    
    class Meta:
        ordering = ['-date', '-time_in']
        unique_together = ['employee', 'date']
    
    @property
    def hours_worked(self):
        """Calculate hours worked (if checked out)"""
        if not self.time_out:
            return None
        
        time_in_dt = timezone.datetime.combine(timezone.now().date(), self.time_in)
        time_out_dt = timezone.datetime.combine(timezone.now().date(), self.time_out)
        
        # Handle overnight shifts
        if time_out_dt < time_in_dt:
            time_out_dt += timezone.timedelta(days=1)
        
        duration = time_out_dt - time_in_dt
        return duration.total_seconds() / 3600  # Convert to hours
    
    @property
    def is_checked_out(self):
        return self.time_out is not None

class Salary(models.Model):
    """Model for tracking employee salaries"""
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salaries')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.username} - {self.amount} (from {self.effective_date})"
    
    class Meta:
        ordering = ['-effective_date']
