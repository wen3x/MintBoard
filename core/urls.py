from django.urls import path
from . import views
from .views import PostDeleteView
from .views import CommentCreateView

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_detail'),
    path('api/load-more/', views.load_more_posts, name='load_more_posts'),
    path('api/like/<uuid:post_id>/', views.like_post, name='like_post'),
    path('create-post/', views.create_post, name='create_post'),
    path('post/<uuid:post_id>/', views.post_detail, name='post_detail'),
    path('post/<uuid:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('post/<uuid:pk>/comment/', CommentCreateView.as_view(), name='add_comment'),
    path('mini-profile/<str:username>/', views.mini_profile, name='mini_profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
]