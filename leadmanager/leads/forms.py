from django import forms
from django.contrib.auth.models import User
from .models import Lead, LeadSource, LeadStatus


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'email', 'phone', 'company', 'job_title', 'source', 'status', 'notes', 'assigned_to']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(LeadForm, self).__init__(*args, **kwargs)
        
        # Limit assigned_to field to only sales reps and managers
        if user:
            if user.profile.role == 'admin':
                self.fields['assigned_to'].queryset = User.objects.filter(
                    profile__role__in=['sales_rep', 'manager']
                )
            elif user.profile.role == 'manager':
                self.fields['assigned_to'].queryset = User.objects.filter(
                    profile__role='sales_rep'
                )
            else:
                self.fields['assigned_to'].queryset = User.objects.filter(id=user.id)


class LeadImportForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Upload Excel (.xlsx) or CSV (.csv) file'
    )
    source = forms.ModelChoiceField(
        queryset=LeadSource.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )


class LeadAssignForm(forms.Form):
    leads = forms.ModelMultipleChoiceField(
        queryset=Lead.objects.filter(assigned_to__isnull=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'list-unstyled'}),
        required=True
    )
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='sales_rep'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )


class FacebookLeadFetchForm(forms.Form):
    ad_account = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    days = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        initial=7,
        min_value=1,
        max_value=30,
        required=True,
        help_text='Number of days to fetch leads for (1-30)'
    )
