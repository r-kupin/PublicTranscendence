from django.utils.deprecation import MiddlewareMixin
from .models import PageView


class PageViewMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            PageView.objects.create(user=request.user, page=request.path)
        return None
