from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from .models import Client, Project, ProjectTask

class ProjectModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client_obj = Client.objects.create(
            name='Test Client',
            email='client@example.com',
            phone='123-456-7890'
        )
        self.project = Project.objects.create(
            name='Test Project',
            client=self.client_obj,
            status='new',
            start_date=date.today()
        )
        self.task = ProjectTask.objects.create(
            name='Test Task',
            project=self.project,
            assigned_to=self.user,
            status='todo'
        )
    
    def test_client_creation(self):
        """Test client creation"""
        self.assertEqual(self.client_obj.name, 'Test Client')
        self.assertEqual(self.client_obj.email, 'client@example.com')
    
    def test_project_creation(self):
        """Test project creation"""
        self.assertEqual(self.project.name, 'Test Project')
        self.assertEqual(self.project.client, self.client_obj)
        self.assertEqual(self.project.status, 'new')
    
    def test_task_creation(self):
        """Test task creation"""
        self.assertEqual(self.task.name, 'Test Task')
        self.assertEqual(self.task.project, self.project)
        self.assertEqual(self.task.assigned_to, self.user)
        self.assertEqual(self.task.status, 'todo')

class ProjectViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client_obj = Client.objects.create(
            name='Test Client',
            email='client@example.com',
            phone='123-456-7890'
        )
        self.project = Project.objects.create(
            name='Test Project',
            client=self.client_obj,
            status='new',
            start_date=date.today()
        )
        self.task = ProjectTask.objects.create(
            name='Test Task',
            project=self.project,
            assigned_to=self.user,
            status='todo'
        )
        
        self.client.login(username='testuser', password='password')
    
    def test_client_list_view(self):
        """Test client list view"""
        response = self.client.get(reverse('client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Client')
        self.assertTemplateUsed(response, 'projects/client_list.html')
    
    def test_project_list_view(self):
        """Test project list view"""
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        self.assertTemplateUsed(response, 'projects/project_list.html')
