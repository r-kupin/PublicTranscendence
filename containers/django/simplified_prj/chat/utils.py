from django.utils import timezone
from datetime import timedelta
from models import PageView


def get_active_users(page_url, minutes=5):
    now = timezone.now()
    time_threshold = now - timedelta(minutes=minutes)
    return PageView.objects.filter(page=page_url, timestamp__gte=time_threshold).values('user').distinct().count()
