from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path('', include('mini_transcendence.urls')),
    path('chat/', include('chat.urls')),
    path('game/', include('game.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
