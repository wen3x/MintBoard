from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter post title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your post content...', 'rows': 10}),
        }