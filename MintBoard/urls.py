from django.contrib import admin
from django.urls import path, include
from core.views import SignUpView
from core.views import SignUpView, home_view

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('', include('core.urls')),
]
