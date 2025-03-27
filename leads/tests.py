from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Lead, LeadSource, LeadStatus

class LeadTestCase(TestCase):
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
        
        # Create lead status and source
        self.status = LeadStatus.objects.create(name='New', order=1)
        self.source = LeadSource.objects.create(name='Website')
        
        # Create a test lead
        self.lead = Lead.objects.create(
            name='Test Lead',
            email='test@example.com',
            phone='1234567890',
            company='Test Company',
            source=self.source,
            status=self.status,
            assigned_to=self.sales_user,
            created_by=self.admin_user
        )
    
    def test_lead_list_view(self):
        # Login as admin
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('leads:lead_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Lead')
        
        # Login as sales rep
        self.client.login(username='salesrep', password='salespassword')
        response = self.client.get(reverse('leads:lead_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Lead')
    
    def test_lead_detail_view(self):
        # Login as admin
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('leads:lead_detail', args=[self.lead.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Lead')
        
        # Login as sales rep
        self.client.login(username='salesrep', password='salespassword')
        response = self.client.get(reverse('leads:lead_detail', args=[self.lead.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Lead')
    
    def test_lead_create_view(self):
        # Login as admin
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('leads:lead_create'))
        self.assertEqual(response.status_code, 200)
        
        # Submit the form
        response = self.client.post(reverse('leads:lead_create'), {
            'name': 'New Lead',
            'email': 'new@example.com',
            'phone': '9876543210',
            'company': 'New Company',
            'source': self.source.pk,
            'status': self.status.pk,
            'notes': 'Test notes'
        })
        self.assertEqual(Lead.objects.count(), 2)
        new_lead = Lead.objects.get(name='New Lead')
        self.assertRedirects(response, reverse('leads:lead_detail', args=[new_lead.pk]))
