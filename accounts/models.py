from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """Extended profile for users with role information"""
    
    # Role choices
    ADMIN = 'admin'
    MANAGER = 'manager'
    SALES_REP = 'sales_rep'
    OPERATIONS_MANAGER = 'operations_manager'
    DEVELOPER = 'developer'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (SALES_REP, 'Sales Representative'),
        (OPERATIONS_MANAGER, 'Operations Manager'),
        (DEVELOPER, 'Developer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=SALES_REP)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def is_admin(self):
        return self.role == self.ADMIN
    
    def is_manager(self):
        return self.role == self.MANAGER
    
    def is_sales_rep(self):
        return self.role == self.SALES_REP
    
    def is_operations_manager(self):
        return self.role == self.OPERATIONS_MANAGER
    
    def is_developer(self):
        return self.role == self.DEVELOPER
