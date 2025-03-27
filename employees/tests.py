from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time
from .models import Attendance, Salary

class EmployeesTestCase(TestCase):
    def setUp(self):
        # Create a test user with admin role
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        self.admin_user.userprofile.role = 'admin'
        self.admin_user.userprofile.save()
        
        # Create a test user with employee role
        self.employee_user = User.objects.create_user(
            username='employee',
            email='employee@example.com',
            password='employeepassword'
        )
        self.employee_user.userprofile.role = 'developer'
        self.employee_user.userprofile.save()
        
        # Create attendance record
        self.attendance = Attendance.objects.create(
            employee=self.employee_user,
            date=timezone.now().date(),
            punch_in_time=time(9, 0),
            status='present'
        )
        
        # Create salary record
        self.salary = Salary.objects.create(
            employee=self.employee_user,
            month=1,
            year=2023,
            amount=5000.00,
            status='paid',
            payment_date=timezone.now().date(),
            created_by=self.admin_user
        )
    
    def test_employee_list_view(self):
        # Login as admin
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('employees:employee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'employee')
    
    def test_attendance_log_view(self):
        # Login as admin
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('employees:attendance_log'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'employee')
        
        # Login as employee
        self.client.login(username='employee', password='employeepassword')
        response = self.client.get(reverse('employees:attendance_log'))
        self.assertEqual(response.status_code, 200)
    
    def test_punch_in_view(self):
        # Login as employee
        self.client.login(username='employee', password='employeepassword')
        
        # Reset attendance for testing
        Attendance.objects.filter(employee=self.employee_user).delete()
        
        response = self.client.get(reverse('employees:punch_in'))
        self.assertRedirects(response, reverse('dashboard:index'))
        
        # Check if attendance was created
        self.assertTrue(Attendance.objects.filter(
            employee=self.employee_user,
            date=timezone.now().date()
        ).exists())
    
    def test_salary_list_view(self):
        # Login as admin
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('employees:salary_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'employee')
        self.assertContains(response, '5000.00')
