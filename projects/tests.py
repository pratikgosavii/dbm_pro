from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from .models import Client, Project, ProjectStatus

class ProjectsTestCase(TestCase):
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
        
        # Create a test user with developer role
        self.dev_user = User.objects.create_user(
            username='developer',
            email='dev@example.com',
            password='devpassword'
        )
        self.dev_user.userprofile.role = 'developer'
        self.dev_user.userprofile.save()
        
        # Create client
        self.client_obj = Client.objects.create(
            name='Test Client',
            email='client@example.com',
            phone='1234567890',
            company='Test Company',
            created_by=self.admin_user
        )
        
        # Create project status
        self.status = ProjectStatus.objects.create(name='In Progress', order=1)
        
        # Create project
        self.project = Project.objects.create(
            name='Test Project',
            client=self.client_obj,
            description='Test Description',
            status=self.status,
            start_date=date.today(),
            budget=10000.00,
            created_by=self.admin_user
        )
        self.project.assigned_developers.add(self.dev_user)
    
    def test_client_list_view(self):
        # Login as admin
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('projects:client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Client')
        
        # Login as ops manager
        self.client.login(username='opsmanager', password='opspassword')
        response = self.client.get(reverse('projects:client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Client')
    
    def test_project_list_view(self):
        # Login as admin
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('projects:project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        
        # Login as developer
        self.client.login(username='developer', password='devpassword')
        response = self.client.get(reverse('projects:project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
    
    def test_project_detail_view(self):
        # Login as admin
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('projects:project_detail', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        
        # Login as developer
        self.client.login(username='developer', password='devpassword')
        response = self.client.get(reverse('projects:project_detail', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
