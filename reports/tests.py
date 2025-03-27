from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from leads.models import Lead, LeadSource, LeadStatus
from projects.models import Project, ProjectStatus, Client
from employees.models import Salary
from payments.models import Payment, PaymentMethod

class ReportsTestCase(TestCase):
    def setUp(self):
        # Create a test user with admin role
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        self.admin_user.userprofile.role = 'admin'
        self.admin_user.userprofile.save()
        
        # Create a test user with manager role
        self.manager_user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='managerpassword'
        )
        self.manager_user.userprofile.role = 'manager'
        self.manager_user.userprofile.save()
        
        # Create a test user with ops_manager role
        self.ops_user = User.objects.create_user(
            username='opsmanager',
            email='ops@example.com',
            password='opspassword'
        )
        self.ops_user.userprofile.role = 'ops_manager'
        self.ops_user.userprofile.save()
        
        # Create lead status and source
        self.lead_status = LeadStatus.objects.create(name='New', order=1)
        self.lead_source = LeadSource.objects.create(name='Website')
        
        # Create a test lead
        self.lead = Lead.objects.create(
            name='Test Lead',
            email='testlead@example.com',
            source=self.lead_source,
            status=self.lead_status,
            created_by=self.admin_user
        )
        
        # Create client and project
        self.client = Client.objects.create(
            name='Test Client',
            email='testclient@example.com',
            created_by=self.admin_user
        )
        
        self.project_status = ProjectStatus.objects.create(name='Active', order=1)
        
        self.project = Project.objects.create(
            name='Test Project',
            client=self.client,
            status=self.project_status,
            start_date=date.today(),
            created_by=self.admin_user
        )
        
        # Create payment method and payment
        self.payment_method = PaymentMethod.objects.create(name='Bank Transfer')
        
        self.payment = Payment.objects.create(
            project=self.project,
            amount=1000.00,
            payment_date=date.today(),
            payment_method=self.payment_method,
            status='completed',
            created_by=self.admin_user
        )
        
        # Create salary
        self.salary = Salary.objects.create(
            employee=self.admin_user,
            month=timezone.now().month,
            year=timezone.now().year,
            amount=5000.00,
            status='paid',
            created_by=self.admin_user
        )
    
    def test_sales_report_access(self):
        # Admin should be able to access
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('reports:sales_report'))
        self.assertEqual(response.status_code, 200)
        
        # Manager should be able to access
        self.client.login(username='manager', password='managerpassword')
        response = self.client.get(reverse('reports:sales_report'))
        self.assertEqual(response.status_code, 200)
        
        # Ops manager should not be able to access
        self.client.login(username='opsmanager', password='opspassword')
        response = self.client.get(reverse('reports:sales_report'))
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
    
    def test_payment_report_access(self):
        # Admin should be able to access
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('reports:payment_report'))
        self.assertEqual(response.status_code, 200)
        
        # Ops manager should be able to access
        self.client.login(username='opsmanager', password='opspassword')
        response = self.client.get(reverse('reports:payment_report'))
        self.assertEqual(response.status_code, 200)
        
        # Manager should not be able to access
        self.client.login(username='manager', password='managerpassword')
        response = self.client.get(reverse('reports:payment_report'))
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
    
    def test_salary_report_access(self):
        # Admin should be able to access
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('reports:salary_report'))
        self.assertEqual(response.status_code, 200)
        
        # Ops manager should be able to access
        self.client.login(username='opsmanager', password='opspassword')
        response = self.client.get(reverse('reports:salary_report'))
        self.assertEqual(response.status_code, 200)
        
        # Manager should not be able to access
        self.client.login(username='manager', password='managerpassword')
        response = self.client.get(reverse('reports:salary_report'))
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
