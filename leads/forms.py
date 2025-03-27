from django import forms
from django.contrib.auth.models import User
from .models import Lead

class LeadForm(forms.ModelForm):
    """Form for creating and updating leads"""
    class Meta:
        model = Lead
        fields = ['first_name', 'last_name', 'email', 'phone', 'company', 
                  'job_title', 'status', 'notes', 'assigned_to']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit assigned_to field to users who are sales reps, managers, or admins
        sales_profiles = User.objects.filter(profile__role__in=['sales_rep', 'manager', 'admin'])
        self.fields['assigned_to'].queryset = sales_profiles
        self.fields['assigned_to'].required = False

class LeadImportForm(forms.Form):
    """Form for importing leads from Excel or Facebook"""
    IMPORT_CHOICES = [
        ('excel', 'Import from Excel'),
        ('facebook', 'Import from Facebook Ads'),
    ]
    
    import_type = forms.ChoiceField(
        choices=IMPORT_CHOICES, 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    excel_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        import_type = cleaned_data.get('import_type')
        excel_file = cleaned_data.get('excel_file')
        
        if import_type == 'excel' and not excel_file:
            raise forms.ValidationError("Please select an Excel file to import.")
        
        return cleaned_data

class LeadFilterForm(forms.Form):
    """Form for filtering leads"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'})
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + list(Lead.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    source = forms.ChoiceField(
        required=False,
        choices=[('', 'All Sources')] + list(Lead.SOURCE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assigned_to = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.filter(profile__role__in=['sales_rep', 'manager', 'admin']),
        empty_label="All Representatives",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
