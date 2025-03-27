from django import forms
from .models import Payment, PaymentMethod

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'project', 'amount', 'payment_date', 
            'payment_method', 'reference_number', 'status', 'notes'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
