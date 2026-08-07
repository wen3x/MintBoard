from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    user = request.user
    context = {
        'user': user,
        'bio': user.profile.bio if hasattr(user, 'profile') else 'No info yet',
    }
    return render(request, 'profile.html', context)

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


def home_view(request):
    return render(request, 'home.html')
