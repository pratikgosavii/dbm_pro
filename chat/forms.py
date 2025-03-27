from django import forms
from django.contrib.auth.models import User
from .models import ChatGroup, Message

class ChatGroupForm(forms.ModelForm):
    """Form for creating and editing chat groups"""
    class Meta:
        model = ChatGroup
        fields = ['name', 'description', 'members']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control border-purple'}),
            'description': forms.Textarea(attrs={'class': 'form-control border-purple', 'rows': 3}),
            'members': forms.SelectMultiple(attrs={'class': 'form-select border-purple', 'size': '5'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ChatGroupForm, self).__init__(*args, **kwargs)
        if user:
            # Exclude the current user from the members field
            self.fields['members'].queryset = User.objects.exclude(id=user.id)

class MessageForm(forms.ModelForm):
    """Form for creating messages"""
    class Meta:
        model = Message
        fields = ['content', 'image', 'document']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control border-purple', 'rows': 3, 'placeholder': 'Type your message...'}),
            'image': forms.FileInput(attrs={'class': 'form-control border-purple'}),
            'document': forms.FileInput(attrs={'class': 'form-control border-purple'}),
        }

class DirectMessageForm(MessageForm):
    """Form for sending direct messages"""
    receiver = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select border-purple'})
    )
    
    class Meta(MessageForm.Meta):
        fields = ['receiver'] + MessageForm.Meta.fields
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DirectMessageForm, self).__init__(*args, **kwargs)
        if user:
            # Exclude the current user from the receiver field
            self.fields['receiver'].queryset = User.objects.exclude(id=user.id)