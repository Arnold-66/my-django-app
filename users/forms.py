from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile



class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', ]

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role', 'location', 'bio','image']
        widget = {
            'content': forms.Textarea(attrs={'rows': 2, 'cols': 100, 'class': 'form-control'}),  # Smaller size
        }