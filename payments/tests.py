from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from .models import Payment, PaymentMethod
from projects.models import Client, Project, ProjectStatus

class PaymentsTestCase(TestCase):
    def setUp(self):
        # Create a test user with admin role
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        self.admin_user.userprofile.role = 'admin'
        self.admin_user.userprofile.save()
        
        # Create a test user with operations manager role
        self.ops_user = User.objects.create_user(
            username='opsmanager',
            email='ops@example.com',
            password='opspassword'
        )
        self.ops_user.userprofile.role = 'ops_manager'
        self.ops_user.userprofile.save()
        
        # Create client
        self.client_obj = Client.objects.create(
            name='Test Client',
            email='client@example.com',
            created_by=self.admin_user
        )
        
        # Create project status
        self.status = ProjectStatus.objects.create(name='Active')
        
        # Create project
        self.project = Project.objects.create(
            name='Test Project',
            client=self.client_obj,
            status=self.status,
            start_date=date.today(),
            created_by=self.admin_user
        )
        
        # Create payment method
        self.payment_method = PaymentMethod.objects.create(name='Bank Transfer')
        
        # Create payment
        self.payment = Payment.objects.create(
            project=self.project,
            amount=1000.00,
            payment_date=date.today(),
            payment_method=self.payment_method,
            status='completed',
            created_by=self.admin_user
        )
    
    def test_payment_list_view(self):
        # Login as admin
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('payments:payment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        self.assertContains(response, '1000.00')
    
    def test_payment_create_view(self):
        # Login as admin
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('payments:payment_create'))
        self.assertEqual(response.status_code, 200)
        
        # Submit the form
        response = self.client.post(reverse('payments:payment_create'), {
            'project': self.project.pk,
            'amount': 500.00,
            'payment_date': date.today().strftime('%Y-%m-%d'),
            'payment_method': self.payment_method.pk,
            'reference_number': 'REF123',
            'status': 'pending',
            'notes': 'Test payment'
        })
        self.assertEqual(Payment.objects.count(), 2)
