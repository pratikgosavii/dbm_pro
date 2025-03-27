from django import forms
from django.contrib.auth.models import User
from .models import Client, Project, Payment

class ClientForm(forms.ModelForm):
    """Form for creating and updating clients"""
    class Meta:
        model = Client
        fields = ['name', 'contact_person', 'email', 'phone', 'address', 'website', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ProjectForm(forms.ModelForm):
    """Form for creating and updating projects"""
    class Meta:
        model = Project
        fields = ['name', 'client', 'description', 'start_date', 'end_date', 
                  'estimated_hours', 'status', 'assigned_developers']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estimated_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_developers': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit assigned_developers field to users who are developers
        developers = User.objects.filter(profile__role='developer')
        self.fields['assigned_developers'].queryset = developers

class PaymentForm(forms.ModelForm):
    """Form for recording and updating payments"""
    class Meta:
        model = Payment
        fields = ['project', 'amount', 'payment_date', 'payment_method', 
                  'description', 'receipt_number']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'receipt_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProjectFilterForm(forms.Form):
    """Form for filtering projects"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'})
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + list(Project.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    client = forms.ModelChoiceField(
        required=False,
        queryset=Client.objects.all(),
        empty_label="All Clients",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    developer = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.filter(profile__role='developer'),
        empty_label="All Developers",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class PaymentFilterForm(forms.Form):
    """Form for filtering payments"""
    project = forms.ModelChoiceField(
        required=False,
        queryset=Project.objects.all(),
        empty_label="All Projects",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    payment_method = forms.ChoiceField(
        required=False,
        choices=[('', 'All Methods')] + list(Payment.PAYMENT_METHOD_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
