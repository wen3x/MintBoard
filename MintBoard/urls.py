from django.contrib import admin
from django.urls import path, include
from core.views import SignUpView
from core.views import SignUpView, home_view
from django.views.generic import TemplateView

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about_page'),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy_page'),
    path('', include('core.urls')),
]
