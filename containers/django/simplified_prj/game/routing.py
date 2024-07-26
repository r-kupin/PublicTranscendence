from django.urls import re_path
from game import consumers

websocket_urlpatterns = [
    re_path(r'wss/game/(?P<match_id>[0-9a-f-]+)/$', consumers.GameConsumer.as_asgi()),
]
