import base64
from contextlib import suppress
import pickle

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models.aggregates import Max
from rest_framework import serializers
import tzlocal
from common.collectionutils.thumbnailer import TIMESTAMP_FORMAT

from gallery.models import Image, Directory, ImageGroup, Video


class SubdirectorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Directory
        fields = ['id', 'path', 'shared', 'parent']


def get_polymorphic_serializer(base_serializer):
    serializer_map = {}
    for serializer in base_serializer.__subclasses__():
        with suppress(AttributeError):
            serializer_map[serializer.Meta.model] = serializer

    class PolymorphicSerializer(serializers.BaseSerializer):
        def to_representation(self, instance):
            instance_serializer = serializer_map[type(instance)]
            data = instance_serializer(instance).data
            return data

    return PolymorphicSerializer


class FileSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    def get_path(self, obj):
        return getattr(obj, 'path')

    def get_type(self, obj):
        return obj.type.split('.')[-1]

    def get_timestamp(self, obj):
        return obj.modification_time.astimezone(tzlocal.get_localzone()).strftime(TIMESTAMP_FORMAT)

    class Meta:
        fields = ['id', 'path', 'type', 'timestamp']

    def update(self, instance, validated_data):
        update_result = super().update(instance, validated_data)
        # when file data is modified, directory's cache has to be purged
        DirectoryJSONCachingStrategy.invalidate_cache(instance.directory)
        return update_result


class ImageSerializer(FileSerializer):
    class Meta:
        model = Image
        fields = FileSerializer.Meta.fields + ['orientation', 'aspect_ratio']


class VideoSerializer(FileSerializer):
    class Meta:
        model = Video
        fields = FileSerializer.Meta.fields


class DirectoryJSONCachingStrategy:
    """
    Returns cached version of directory if neither directory nor file has been modified
    since relevant cache entry has been added.
    Otherwise new value is calculated and inserted to cache.
    """
    CREATION_TIME_KEY = 'cache_creation_time'
    REPRESENTATION_KEY = 'representation'
    CACHE_ENTRY_KEY = 'directory_{}'

    @classmethod
    def invalidate_cache(cls, directory):
        cache.delete(cls.CACHE_ENTRY_KEY.format(directory.path))

    @classmethod
    def encode_representation(cls, instance, representation, mtime):
        cache_entry = {cls.CREATION_TIME_KEY: mtime,
                       cls.REPRESENTATION_KEY: representation}
        return cache_entry

    @staticmethod
    def decode_representation(cached_data):
        return cached_data

    @classmethod
    def wrap(cls, to_representation):
        def cached_to_representation(self, instance):
            # calculate mtime for directory (take files and directory itself into account)
            if instance.files.count() > 0:
                files_max_mtime = instance.files.aggregate(mtime=Max('modification_time'))['mtime']
                mtime = max(files_max_mtime, instance.modification_time)
            else:
                mtime = instance.modification_time

            instance_key = cls.CACHE_ENTRY_KEY.format(instance.path)

            # try to fetch cached representation
            cached_data = cache.get(instance_key, None)
            if cached_data:
                cached_object = cls.decode_representation(cached_data)
                if cached_object[cls.CREATION_TIME_KEY] >= mtime:
                    # cache hit - return result from cache
                    return cached_object[cls.REPRESENTATION_KEY]

            # cache miss: calculate new representation, store it in cache
            representation = to_representation(self, instance)
            cache.set(instance_key, cls.encode_representation(instance, representation, mtime), None)

            return representation

        return cached_to_representation


class ImageGroupSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = ImageGroup

    def get_images(self, obj):
        images_queryset = obj.images \
            .exclude(directory__path__iexact='Trash') \
            .exclude(directory__path__startswith='Trash/')
        return ImageSerializer(images_queryset, many=True).data


class DirectorySerializer(SubdirectorySerializer):
    subdirectories = SubdirectorySerializer(many=True)
    files = serializers.SerializerMethodField()

    # return entries from cache if no change to directory or files within occurred
    @DirectoryJSONCachingStrategy.wrap
    def to_representation(self, instance):
        return super().to_representation(instance)

    class Meta:
        model = Directory
        fields = SubdirectorySerializer.Meta.fields + ['files', 'subdirectories']

    def get_files(self, obj):
        return get_polymorphic_serializer(FileSerializer)(obj.files.all(), many=True).data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')
