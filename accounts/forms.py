from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, EmployeeCategory

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control border-purple', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control border-purple', 'placeholder': 'Password'})
    )

class EmployeeCategoryForm(forms.ModelForm):
    class Meta:
        model = EmployeeCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control border-purple'}),
            'description': forms.Textarea(attrs={'class': 'form-control border-purple', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
class EmployeeCreationForm(UserCreationForm):
    """Form for creating new employees with associated user profiles"""
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control border-purple'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control border-purple'})
    )
    email = forms.EmailField(
        max_length=254, 
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control border-purple'})
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select border-purple'})
    )
    category = forms.ModelChoiceField(
        queryset=EmployeeCategory.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select border-purple'})
    )
    phone = forms.CharField(
        max_length=15, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control border-purple'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control border-purple', 'rows': 3})
    )
    profile_picture = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control border-purple'})
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 
            'password1', 'password2', 'role', 'category', 'phone', 
            'address', 'profile_picture'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control border-purple'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(EmployeeCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control border-purple'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control border-purple'})

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control border-purple'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control border-purple'})
    )
    email = forms.EmailField(
        max_length=254, 
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control border-purple'})
    )
    
    class Meta:
        model = UserProfile
        fields = ('role', 'category', 'phone', 'address', 'profile_picture')
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select border-purple'}),
            'category': forms.Select(attrs={'class': 'form-select border-purple'}),
            'phone': forms.TextInput(attrs={'class': 'form-control border-purple'}),
            'address': forms.Textarea(attrs={'class': 'form-control border-purple', 'rows': 3}),
            'profile_picture': forms.URLInput(attrs={'class': 'form-control border-purple'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        profile = super(UserProfileForm, self).save(commit=False)
        profile.user.first_name = self.cleaned_data['first_name']
        profile.user.last_name = self.cleaned_data['last_name']
        profile.user.email = self.cleaned_data['email']
        profile.user.save()
        
        if commit:
            profile.save()
        return profile
