from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class DashboardTestCase(TestCase):
    def setUp(self):
        # Create a test user with admin role
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        self.admin_user.userprofile.role = 'admin'
        self.admin_user.userprofile.save()
        
        # Create a test user with sales rep role
        self.sales_user = User.objects.create_user(
            username='salesrep',
            email='salesrep@example.com',
            password='salespassword'
        )
        self.sales_user.userprofile.role = 'sales_rep'
        self.sales_user.userprofile.save()
    
    def test_dashboard_access(self):
        # Login required should redirect to login page
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Admin user should access
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        
        # Sales rep should access
        self.client.login(username='salesrep', password='salespassword')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
