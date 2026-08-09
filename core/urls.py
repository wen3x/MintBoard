from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_detail'),
    path('api/load-more/', views.load_more_posts, name='load_more_posts'),
    path('api/like/<uuid:post_id>/', views.like_post, name='like_post'),
    path('create-post/', views.create_post, name='create_post'),
    path('post/<uuid:post_id>/', views.post_detail, name='post_detail'),
]