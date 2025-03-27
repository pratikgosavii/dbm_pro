from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Attendance, Salary, EmployeeTask, LeaveApplication

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'punch_in_time', 'punch_out_time', 'status', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'punch_in_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'punch_out_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PunchForm(forms.Form):
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

class SalaryForm(forms.ModelForm):
    calculate_from_attendance = forms.BooleanField(
        required=False, 
        initial=True,
        label="Calculate based on attendance",
        help_text="If checked, salary will be calculated based on attendance records",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Salary
        fields = [
            'employee', 'month', 'year', 'base_salary',
            'bonus', 'deduction', 'status', 
            'days_present', 'working_days',
            'payment_date', 'notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'month': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bonus': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'deduction': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'days_present': forms.NumberInput(attrs={'class': 'form-control'}),
            'working_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make amount read-only if it's calculated from attendance
        if self.instance.pk:
            self.fields['days_present'].widget.attrs['readonly'] = True
            self.fields['working_days'].widget.attrs['readonly'] = True
        
        # Add help text
        self.fields['base_salary'].help_text = "Monthly base salary (before attendance calculation)"
        self.fields['days_present'].help_text = "Number of days the employee was present"
        self.fields['working_days'].help_text = "Total working days in the month"
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # If form indicates to calculate from attendance
        if self.cleaned_data.get('calculate_from_attendance'):
            instance.calculate_salary()
        else:
            # If not calculating from attendance but manually setting days_present/working_days
            # Calculate the amount based on the manually entered values
            if instance.working_days > 0:
                daily_rate = instance.base_salary / instance.working_days
                instance.amount = round(daily_rate * instance.days_present, 2)
            else:
                instance.amount = 0
                
        if commit:
            instance.save()
            
        return instance

class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = [
            'leave_type', 'start_date', 'end_date', 'reason'
        ]
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Please provide reason for leave'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set min date for leave application to today
        today = timezone.now().date().isoformat()
        self.fields['start_date'].widget.attrs['min'] = today
        self.fields['end_date'].widget.attrs['min'] = today
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            # Validate that end date is not before start date
            if end_date < start_date:
                raise ValidationError('End date cannot be before start date')
            
            # Validate that dates are not in the past
            today = timezone.now().date()
            if start_date < today:
                raise ValidationError('Cannot apply for leave in the past')
        
        return cleaned_data

class LeaveResponseForm(forms.ModelForm):
    """Form for admins/managers to respond to leave applications"""
    class Meta:
        model = LeaveApplication
        fields = ['status', 'admin_remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add remarks about this leave application'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limit status choices to just approved/declined/cancelled
        self.fields['status'].choices = [
            ('approved', 'Approved'),
            ('declined', 'Declined'),
            ('cancelled', 'Cancelled')
        ]
        
        # Mark status as required
        self.fields['status'].required = True

class EmployeeTaskForm(forms.ModelForm):
    class Meta:
        model = EmployeeTask
        fields = [
            'title', 'description', 'assigned_to', 'priority',
            'status', 'start_date', 'due_date', 'notes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed description of the task'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes or instructions'})
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and not user.userprofile.is_admin and not user.userprofile.is_manager:
            self.fields['assigned_to'].queryset = User.objects.filter(pk=user.pk)
