from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('sales_rep', 'Sales Representative'),
        ('ops_manager', 'Operations Manager'),
        ('developer', 'Developer'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='sales_rep')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_manager(self):
        return self.role == 'manager'
    
    @property
    def is_sales_rep(self):
        return self.role == 'sales_rep'
    
    @property
    def is_ops_manager(self):
        return self.role == 'ops_manager'
    
    @property
    def is_developer(self):
        return self.role == 'developer'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()
    except Exception as e:
        print(f"Error saving user profile: {e}")
        pass
