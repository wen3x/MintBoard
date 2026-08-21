from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
import uuid

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True, verbose_name="About me")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Avatar")
    karma = models.IntegerField(default=0, verbose_name="Karma")

    def __str__(self):
        return self.username

class Post(models.Model):
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    title = models.CharField(
        max_length=100,
    )

    description = models.CharField(
        max_length=2000,
        default="No description provided"
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Author'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date'
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_posts',
        blank=True,
        verbose_name='Likes'
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:post_detail', args=[str(self.id)])

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(verbose_name='Comment text')
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} to {self.post}'

class SiteConfig(models.Model):

    SITE_NAME = models.CharField(max_length=20, default="MintBoard")
    
    ACCENT_COLOR = models.CharField(
        max_length=7, 
        default="#2ECC71", 
        verbose_name="Accent color (HEX)"
    )
    
    BACKGROUND_COLOR = models.CharField(
        max_length=7, 
        default="#ffffff", 
        verbose_name="Background color (HEX)"
    )
    
    LOGO = models.FileField(
        upload_to='site/logo/',
        validators=[FileExtensionValidator(allowed_extensions=['svg'])],
        verbose_name="Logo (SVG)",
        blank=True,
        null=True
    )
    
    FAVICON = models.FileField(
        upload_to='site/favicon/',
        validators=[
            FileExtensionValidator(allowed_extensions=['svg']), 
        ],
        verbose_name="Favicon (SVG)",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def save(self, *args, **kwargs):
        if not self.pk and SiteConfig.objects.exists():
            raise ValidationError("One copy of this model only.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return "Site Settings"