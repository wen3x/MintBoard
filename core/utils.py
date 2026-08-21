from .models import Notification

def create_notification(recipient, actor, verb, target_url=None, target_title=None):
    if recipient == actor:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        target_url=target_url,
        target_title=target_title
    )