from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django_svg_image_form_field import SvgAndImageFormField
from .models import Post, SiteConfig, User

admin.site.register(User, UserAdmin)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)

class SiteConfigForm(forms.ModelForm):
    LOGO = SvgAndImageFormField(required=False, label="Logo (SVG)")
    FAVICON = SvgAndImageFormField(required=False, label="Favicon (SVG)")

    class Meta:
        model = SiteConfig
        fields = '__all__'
        widgets = {
            'ACCENT_COLOR': forms.TextInput(attrs={'type': 'color', 'style': 'height: 40px; width: 100px;'}),
            'BACKGROUND_COLOR': forms.TextInput(attrs={'type': 'color', 'style': 'height: 40px; width: 100px;'}),
        }

@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    form = SiteConfigForm

    def has_add_permission(self, request):
        if SiteConfig.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False