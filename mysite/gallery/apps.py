from django.apps.config import AppConfig
from gallery.caching import DirectoryJSONCachingStrategy


class GalleryAppConfig(AppConfig):
    name = 'gallery'

    def ready(self):
        DirectoryJSONCachingStrategy.register_signals()