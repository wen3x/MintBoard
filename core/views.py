from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Count, Exists, OuterRef
from .forms import CustomUserCreationForm
from .models import Post, SiteConfig

User = get_user_model()

def get_site_config():
    config, created = SiteConfig.objects.get_or_create(
        defaults={
            'SITE_NAME': 'MintBoard',
            'ACCENT_COLOR': '#2ECC71',
            'BACKGROUND_COLOR': '#ffffff'
        }
    )
    return config

def home_view(request):
    config = get_site_config()
    user = request.user if request.user.is_authenticated else None
    posts = Post.objects.select_related('author').annotate(
        likes_count=Count('likes'),
        user_liked=Exists(Post.likes.through.objects.filter(
            post_id=OuterRef('id'), user_id=user.id
        )) if user else None
    ).order_by('-created_at')[:10]

    if user is None:
        for post in posts:
            post.user_liked = False

    context = {
        'posts': posts,
        'config': config,
    }
    return render(request, 'home.html', context)

@login_required
def profile_view(request, username=None):
    config = get_site_config()
    if username:
        user_profile = get_object_or_404(User, username=username)
    else:
        user_profile = request.user

    posts = Post.objects.filter(author=user_profile).annotate(
        likes_count=Count('likes'),
        user_liked=Exists(Post.likes.through.objects.filter(
            post_id=OuterRef('id'), user_id=request.user.id
        ))
    ).order_by('-created_at')

    context = {
        'profile_user': user_profile,
        'posts': posts,
        'config': config,
        'is_own_profile': request.user == user_profile,
    }
    return render(request, 'profile.html', context)

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@login_required
def load_more_posts(request):
    page = int(request.GET.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    user = request.user
    posts = Post.objects.select_related('author').annotate(
        likes_count=Count('likes'),
        user_liked=Exists(Post.likes.through.objects.filter(
            post_id=OuterRef('id'), user_id=user.id
        ))
    ).order_by('-created_at')[offset:offset + per_page]

    if not posts:
        return HttpResponse('')

    html = render_to_string('partials/post_list.html', {'posts': posts})
    return HttpResponse(html)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    context = {
        'post': post,
        'liked': liked,
        'likes_count': post.likes.count(),
    }
    html = render_to_string('partials/like_button.html', context, request=request)
    return HttpResponse(html)

@login_required
def create_post(request):
    return HttpResponse('Create post form')