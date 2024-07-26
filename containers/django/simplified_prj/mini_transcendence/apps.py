from django.apps import AppConfig


class MiniTranscendenceConfig(AppConfig):
    name = 'mini_transcendence'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from . import signals
