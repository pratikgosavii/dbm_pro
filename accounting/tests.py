from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from projects.models import Client, Project
from .models import Payment, Invoice, ExpenseCategory, Expense

class AccountingModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client_obj = Client.objects.create(name='Test Client')
        self.project = Project.objects.create(
            name='Test Project', 
            client=self.client_obj,
            status='in_progress',
            start_date=date.today()
        )
        self.invoice = Invoice.objects.create(
            invoice_number='INV-001',
            project=self.project,
            amount=1000.00,
            issue_date=date.today(),
            due_date=date.today().replace(day=date.today().day + 30),
            status='sent'
        )
        self.payment = Payment.objects.create(
            project=self.project,
            invoice=self.invoice,
            amount=500.00,
            payment_date=date.today(),
            payment_method='bank_transfer',
            received_by=self.user
        )
        self.category = ExpenseCategory.objects.create(name='Office Supplies')
        self.expense = Expense.objects.create(
            description='Office chairs',
            amount=200.00,
            expense_date=date.today(),
            category=self.category,
            project=self.project,
            created_by=self.user
        )

    def test_invoice_creation(self):
        """Test invoice creation"""
        self.assertEqual(self.invoice.invoice_number, 'INV-001')
        self.assertEqual(self.invoice.project, self.project)
        self.assertEqual(self.invoice.amount, 1000.00)
        self.assertEqual(self.invoice.status, 'sent')

    def test_payment_creation(self):
        """Test payment creation"""
        self.assertEqual(self.payment.project, self.project)
        self.assertEqual(self.payment.invoice, self.invoice)
        self.assertEqual(self.payment.amount, 500.00)
        self.assertEqual(self.payment.payment_method, 'bank_transfer')
        self.assertEqual(self.payment.received_by, self.user)

    def test_expense_creation(self):
        """Test expense creation"""
        self.assertEqual(self.expense.description, 'Office chairs')
        self.assertEqual(self.expense.amount, 200.00)
        self.assertEqual(self.expense.category, self.category)
        self.assertEqual(self.expense.project, self.project)
        self.assertEqual(self.expense.created_by, self.user)
        self.assertFalse(self.expense.approved)

    def test_payment_updates_invoice_status(self):
        """Test that payment updates invoice status when fully paid"""
        # Add another payment to fully pay the invoice
        Payment.objects.create(
            project=self.project,
            invoice=self.invoice,
            amount=500.00,
            payment_date=date.today(),
            payment_method='bank_transfer',
            received_by=self.user
        )
        
        # Refresh invoice from database
        self.invoice.refresh_from_db()
        
        # Invoice should now be marked as paid
        self.assertEqual(self.invoice.status, 'paid')
