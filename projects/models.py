from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Client(models.Model):
    """Client model for storing client information"""
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Project(models.Model):
    """Project model for storing project information"""
    
    # Project status choices
    NEW = 'new'
    IN_PROGRESS = 'in_progress'
    ON_HOLD = 'on_hold'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (NEW, 'New'),
        (IN_PROGRESS, 'In Progress'),
        (ON_HOLD, 'On Hold'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    name = models.CharField(max_length=100)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    estimated_hours = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NEW)
    assigned_developers = models.ManyToManyField(
        User, 
        related_name='assigned_projects',
        limit_choices_to={'profile__role': 'developer'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.client.name}"
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def is_completed(self):
        return self.status == self.COMPLETED
    
    @property
    def is_active(self):
        return self.status in [self.NEW, self.IN_PROGRESS]
    
    @property
    def total_payments(self):
        return sum(payment.amount for payment in self.payments.all())
    
    @property
    def payments_due(self):
        # Calculate outstanding payments
        # This is a simple implementation; a real one might be more complex
        return self.budget - self.total_payments if hasattr(self, 'budget') else 0

class Payment(models.Model):
    """Payment model for tracking project payments"""
    
    # Payment method choices
    CASH = 'cash'
    BANK_TRANSFER = 'bank_transfer'
    CREDIT_CARD = 'credit_card'
    PAYPAL = 'paypal'
    OTHER = 'other'
    
    PAYMENT_METHOD_CHOICES = [
        (CASH, 'Cash'),
        (BANK_TRANSFER, 'Bank Transfer'),
        (CREDIT_CARD, 'Credit Card'),
        (PAYPAL, 'PayPal'),
        (OTHER, 'Other'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    description = models.CharField(max_length=200, blank=True, null=True)
    receipt_number = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.project.name} - {self.amount} ({self.payment_date})"
    
    class Meta:
        ordering = ['-payment_date']
