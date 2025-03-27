from django import forms
from django.contrib.auth.models import User
from .models import Lead, LeadSource, LeadStatus

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'email', 'phone', 'company', 'source', 'status', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LeadAssignForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['assigned_to']
        widgets = {
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(LeadAssignForm, self).__init__(*args, **kwargs)
        # Only show sales reps in the dropdown
        self.fields['assigned_to'].queryset = User.objects.filter(
            userprofile__role='sales_rep'
        )

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel File',
        help_text='Upload an Excel file with lead data.',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
