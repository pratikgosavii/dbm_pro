from django import forms
from django.utils import timezone
from .models import Payment, Invoice, ExpenseCategory, Expense

class PaymentForm(forms.ModelForm):
    """Form for creating and editing payments"""
    class Meta:
        model = Payment
        fields = ['project', 'invoice', 'amount', 'payment_date', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'invoice': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['payment_date'].initial = timezone.now().date()
        
        # Update invoice queryset based on selected project
        if 'project' in self.data:
            try:
                project_id = int(self.data.get('project'))
                self.fields['invoice'].queryset = Invoice.objects.filter(project_id=project_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.project:
            self.fields['invoice'].queryset = Invoice.objects.filter(project=self.instance.project)
        else:
            self.fields['invoice'].queryset = Invoice.objects.none()

class InvoiceForm(forms.ModelForm):
    """Form for creating and editing invoices"""
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'project', 'amount', 'issue_date', 'due_date', 'status', 'notes']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        today = timezone.now().date()
        self.fields['issue_date'].initial = today
        self.fields['due_date'].initial = today.replace(day=today.day + 30)
        
        # Generate invoice number if creating new invoice
        if not self.instance.pk:
            last_invoice = Invoice.objects.order_by('-id').first()
            last_number = 1
            if last_invoice and last_invoice.invoice_number.startswith('INV-'):
                try:
                    last_number = int(last_invoice.invoice_number[4:]) + 1
                except ValueError:
                    pass
            self.fields['invoice_number'].initial = f'INV-{last_number:06d}'

class ExpenseForm(forms.ModelForm):
    """Form for creating and editing expenses"""
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'expense_date', 'category', 'project', 'receipt']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        self.fields['expense_date'].initial = timezone.now().date()

class DateRangeFilterForm(forms.Form):
    """Form for filtering payments and expenses by date range"""
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        super(DateRangeFilterForm, self).__init__(*args, **kwargs)
        today = timezone.now().date()
        self.fields['start_date'].initial = today.replace(day=1)  # First day of current month
        self.fields['end_date'].initial = today
