from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Count, Exists, OuterRef, Value, BooleanField
from .forms import CustomUserCreationForm, PostForm
from .models import Post, SiteConfig
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

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
    
    # Базовый queryset
    posts = Post.objects.select_related('author').annotate(
        likes_count=Count('likes')
    )
    
    # Добавляем user_liked только если пользователь авторизован
    if user and user.is_authenticated:
        posts = posts.annotate(
            user_liked=Exists(Post.likes.through.objects.filter(
                post_id=OuterRef('id'), user_id=user.id
            ))
        )
    else:
        # Для неавторизованных пользователей ставим False
        posts = posts.annotate(
            user_liked=Value(False, output_field=BooleanField())
        )
    
    posts = posts.order_by('-created_at')[:10]

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
    
    username = request.GET.get('username')
    posts_query = Post.objects.select_related('author')
    
    if username:
        posts_query = posts_query.filter(author__username=username)
    
    posts = posts_query.annotate(
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
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('core:post_detail', post_id=post.id)
    else:
        form = PostForm()
    
    config = get_site_config()
    return render(request, 'create_post.html', {'form': form, 'config': config})

def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author'), id=post_id)
    user = request.user if request.user.is_authenticated else None

    if user and user.is_authenticated:
        post.user_liked = post.likes.filter(id=user.id).exists()
    else:
        post.user_liked = False
    
    post.likes_count = post.likes.count()
    config = get_site_config()
    
    return render(request, 'post_detail.html', {'post': post, 'config': config})

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'
    success_url = reverse_lazy('core:home')