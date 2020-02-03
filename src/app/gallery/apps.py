from django.apps import AppConfig


class GalleryConfig(AppConfig):
    name = 'app.gallery'

    def ready(self):
        from . import signals  # noqa
