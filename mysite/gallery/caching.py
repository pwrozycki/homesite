from django.core.cache import cache
from django.db.models.signals import pre_delete, pre_save

from gallery.models import File, Directory


class DirectoryJSONCachingStrategy:
    """
    Returns cached version of directory.
    Otherwise new value is calculated and inserted to cache.
    """
    CACHE_ENTRY_KEY = 'directory_{}_{}'

    @classmethod
    def on_directory_save(cls, sender, **kwargs):
        directory = kwargs['instance']
        cls.invalidate_cache(directory)

    @classmethod
    def on_mediafile_save(cls, sender, **kwargs):
        file = kwargs['instance']
        cls.invalidate_cache(file.directory)

    @classmethod
    def on_mediafile_delete(cls, sender, **kwargs):
        file = kwargs['instance']
        cls.invalidate_cache(file.directory)

    @classmethod
    def invalidate_cache(cls, directory):
        cache.delete_pattern(cls.CACHE_ENTRY_KEY.format(directory.id, '*'))

    @classmethod
    def wrap(cls, to_representation):
        def cached_to_representation(self, instance):
            username = self.context['request'].user.username
            instance_key = cls.CACHE_ENTRY_KEY.format(instance.id, username)

            # try to fetch cached representation
            cached_representation = cache.get(instance_key, None)
            if cached_representation:
                # cache hit - return result from cache
                return cached_representation

            # cache miss: calculate new representation, store it in cache
            representation = to_representation(self, instance)
            cache.set(instance_key, representation, None)

            return representation

        return cached_to_representation

    @classmethod
    def register_signals(cls):
        for sender in File.__subclasses__():
            pre_save.connect(cls.on_mediafile_save, sender=sender)
            pre_delete.connect(cls.on_mediafile_delete, sender=sender)

        pre_save.connect(cls.on_directory_save, sender=Directory)
