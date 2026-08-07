from .models import SiteConfig

def site_settings(request):
    settings = SiteConfig.objects.first()
    return {
        'site_settings': settings,
    }