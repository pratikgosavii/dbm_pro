from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Lead, LeadStatus, LeadSource

class LeadModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.status = LeadStatus.objects.create(name='New', order=1)
        self.source = LeadSource.objects.create(name='Website')
        
        self.lead = Lead.objects.create(
            name='Test Lead',
            email='test@example.com',
            phone='123-456-7890',
            status=self.status,
            source=self.source,
            created_by=self.user
        )
    
    def test_lead_creation(self):
        """Test lead creation"""
        self.assertEqual(self.lead.name, 'Test Lead')
        self.assertEqual(self.lead.email, 'test@example.com')
        self.assertEqual(self.lead.status, self.status)
    
    def test_lead_str(self):
        """Test lead string representation"""
        self.assertEqual(str(self.lead), 'Test Lead')

class LeadViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.status = LeadStatus.objects.create(name='New', order=1)
        self.source = LeadSource.objects.create(name='Website')
        
        self.lead = Lead.objects.create(
            name='Test Lead',
            email='test@example.com',
            phone='123-456-7890',
            status=self.status,
            source=self.source,
            created_by=self.user
        )
        
        self.client.login(username='testuser', password='password')
    
    def test_lead_list_view(self):
        """Test lead list view"""
        response = self.client.get(reverse('lead_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Lead')
        self.assertTemplateUsed(response, 'leads/lead_list.html')
    
    def test_lead_detail_view(self):
        """Test lead detail view"""
        response = self.client.get(reverse('lead_detail', args=[self.lead.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Lead')
        self.assertContains(response, 'test@example.com')
        self.assertTemplateUsed(response, 'leads/lead_detail.html')
