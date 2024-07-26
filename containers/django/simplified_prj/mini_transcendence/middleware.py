from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone


# prevent caching when user is not authenticated
class DisableClientSideCachingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response


class OnlineUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            now = timezone.now()
            # Update last seen timestamp
            request.user.last_login = now
            request.user.save()
