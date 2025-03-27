from django import forms
from django.contrib.auth.models import User
from projects.models import Project
from .models import Task, Attendance, Salary
from accounts.models import UserProfile

class TaskForm(forms.ModelForm):
    """Form for creating and updating tasks"""
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'project', 'priority', 'status', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Allow restricting available fields
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        
        if fields:
            # Keep only the specified fields
            allowed = set(fields)
            for field in list(self.fields):
                if field not in allowed:
                    self.fields.pop(field)
                    
        # Set queryset for assigned_to to include only active employees
        if 'assigned_to' in self.fields:
            self.fields['assigned_to'].queryset = User.objects.filter(profile__isnull=False)

class AttendanceForm(forms.ModelForm):
    """Form for managing attendance records"""
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'time_in', 'time_out', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_in': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'time_out': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class SalaryForm(forms.ModelForm):
    """Form for managing salary records"""
    class Meta:
        model = Salary
        fields = ['employee', 'amount', 'effective_date', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set queryset for employee to include only active employees
        self.fields['employee'].queryset = User.objects.filter(profile__isnull=False)

class TaskFilterForm(forms.Form):
    """Form for filtering tasks"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'})
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + list(Task.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    priority = forms.ChoiceField(
        required=False,
        choices=[('', 'All Priorities')] + list(Task.PRIORITY_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assigned_to = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.filter(profile__isnull=False),
        empty_label="All Employees",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    project = forms.ModelChoiceField(
        required=False,
        queryset=Project.objects.all(),
        empty_label="All Projects",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class EmployeeFilterForm(forms.Form):
    """Form for filtering employees"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'})
    )
    
    role = forms.ChoiceField(
        required=False,
        choices=[('', 'All Roles')] + list(UserProfile.ROLE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
