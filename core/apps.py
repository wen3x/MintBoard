from django.apps import AppConfig
from django.db.utils import OperationalError

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        try:
            from .models import SiteConfig
            SiteConfig.objects.get_or_create(
                defaults={
                    'SITE_NAME': 'MintBoard',
                    'ACCENT_COLOR': '#2ECC71',
                    'BACKGROUND_COLOR': '#ffffff'
                }
            )
        except OperationalError:
            pass