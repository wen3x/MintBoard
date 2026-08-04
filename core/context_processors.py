from .models import SiteConfig

def site_settings(request):
    """Передает настройки сайта во все шаблоны"""
    settings = SiteConfig.objects.first()
    return {
        'site_settings': settings,
    }