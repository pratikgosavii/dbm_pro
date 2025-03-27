from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }


class RoleAssignmentForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=settings.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
