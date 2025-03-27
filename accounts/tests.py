from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile

class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        
    def test_user_profile_created(self):
        """Test that a user profile is automatically created"""
        self.assertTrue(hasattr(self.user, 'userprofile'))
        self.assertEqual(self.user.userprofile.role, 'sales_rep')  # Default role
        
    def test_has_role_method(self):
        """Test the has_role method"""
        self.user.userprofile.role = 'admin'
        self.user.userprofile.save()
        
        self.assertTrue(self.user.userprofile.has_role('admin'))
        self.assertFalse(self.user.userprofile.has_role('manager'))

class LoginViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
    def test_login_view(self):
        """Test the login view"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        
    def test_login_success(self):
        """Test successful login redirects to dashboard"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('dashboard'))
