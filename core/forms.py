from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import user

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = user
        fields = ('username', 'email')