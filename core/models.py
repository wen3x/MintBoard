from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
import uuid

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

class User(AbstractUser):  # Изменено с user на User
    bio = models.TextField(max_length=500, blank=True, verbose_name="About me")

    def __str__(self):
        return self.username