from .models import SiteConfig

def site_settings(request):
    settings = SiteConfig.objects.first()
    return {
        'site_settings': settings,
    }

def unread_notifications(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(read=False).count()
    else:
        count = 0
    return {'unread_notifications_count': count}