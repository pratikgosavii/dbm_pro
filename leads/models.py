from django.db import models
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Lead(models.Model):
    """Lead model for storing lead information"""
    
    # Lead status choices
    NEW = 'new'
    CONTACTED = 'contacted'
    QUALIFIED = 'qualified'
    PROPOSAL = 'proposal'
    NEGOTIATION = 'negotiation'
    WON = 'won'
    LOST = 'lost'
    
    STATUS_CHOICES = [
        (NEW, 'New'),
        (CONTACTED, 'Contacted'),
        (QUALIFIED, 'Qualified'),
        (PROPOSAL, 'Proposal'),
        (NEGOTIATION, 'Negotiation'),
        (WON, 'Won'),
        (LOST, 'Lost'),
    ]
    
    # Lead source choices
    FACEBOOK = 'facebook'
    EXCEL_IMPORT = 'excel'
    MANUAL = 'manual'
    
    SOURCE_CHOICES = [
        (FACEBOOK, 'Facebook Ads'),
        (EXCEL_IMPORT, 'Excel Import'),
        (MANUAL, 'Manual Entry'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NEW)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=MANUAL)
    notes = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_leads'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    facebook_lead_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company}"
    
    class Meta:
        ordering = ['-created_at']
        
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
        
    @property
    def is_won(self):
        return self.status == self.WON
        
    @property
    def is_lost(self):
        return self.status == self.LOST
        
    @property
    def is_active(self):
        return self.status not in [self.WON, self.LOST]

class LeadActivity(models.Model):
    """Track activities related to a lead"""
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.activity_type} for {self.lead}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Lead Activities'
