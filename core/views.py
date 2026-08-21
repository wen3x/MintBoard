from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Count, Exists, OuterRef, Value, BooleanField
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView
from django.http import JsonResponse
from django.template.loader import render_to_string
from .utils import create_notification

from .forms import CustomUserCreationForm, PostForm, CommentForm
from .models import Post, SiteConfig, Comment, Notification

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
        likes_count=Count('likes')
    )

    if user and user.is_authenticated:
        posts = posts.annotate(
            user_liked=Exists(Post.likes.through.objects.filter(
                post_id=OuterRef('id'), user_id=user.id
            ))
        )
    else:
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

    if liked:
        create_notification(
            recipient=post.author,
            actor=user,
            verb="liked your post",
            target_url=post.get_absolute_url(),
            target_title=post.title
        )

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
    comments = post.comments.all()

    if request.user.is_authenticated:
        post.user_liked = post.likes.filter(id=request.user.id).exists()
    else:
        post.user_liked = False
        # Easter Egg

    post.likes_count = post.likes.count()
    config = get_site_config()
    form = CommentForm()

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'config': config,
        'form': form,
    })

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'
    success_url = reverse_lazy('core:home')

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']

    def get(self, request, *args, **kwargs):
        return redirect('core:post_detail', post_id=self.kwargs['pk'])

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.post = post
        form.instance.author = self.request.user
        comment = form.save()

        if post.author != self.request.user:
            create_notification(
                recipient=post.author,
                actor=self.request.user,
                verb="commented on your post",
                target_url=post.get_absolute_url(),
                target_title=post.title
            )

        if comment.parent and comment.parent.author != self.request.user:
            create_notification(
                recipient=comment.parent.author,
                actor=self.request.user,
                verb="replied to your comment",
                target_url=post.get_absolute_url(),
                target_title=post.title
            )

        return super().form_valid(form)

    def get_success_url(self):
        return self.object.post.get_absolute_url()

def mini_profile(request, username):
    user = get_object_or_404(User, username=username)
    html = render_to_string('partials/mini_profile.html', {'user': user})
    return JsonResponse({'html': html})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Notification

@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications.html', context)

@login_required
def mark_notifications_read(request):
    request.user.notifications.filter(read=False).update(read=True)
    return redirect('core:notifications')