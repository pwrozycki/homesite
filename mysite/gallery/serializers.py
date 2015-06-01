from contextlib import suppress

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from common import debugtool

from gallery.models import Image, Directory, ImageGroup, Video


class SubdirectorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Directory
        fields = ['id', 'path', 'shared', 'parent']


class PolymorphicSerializer(serializers.BaseSerializer):
    def __init__(self, *args, **kwargs):
        base_serializer = kwargs.pop('base_serializer')

        self._serializer_map = {}
        for serializer in base_serializer.__subclasses__():
            with suppress(AttributeError):
                self._serializer_map[serializer.Meta.model] = serializer

        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        serializer = self._serializer_map[type(instance)]
        data = serializer(instance).data
        return data


class FileSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_path(self, obj):
        return getattr(obj, 'path')

    def get_type(self, obj):
        return obj.type.split('.')[-1]

    class Meta:
        fields = ['id', 'path', 'type']


class ImageSerializer(FileSerializer):
    class Meta:
        model = Image
        fields = FileSerializer.Meta.fields + ['orientation']


class VideoSerializer(FileSerializer):
    class Meta:
        model = Video
        fields = FileSerializer.Meta.fields


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

    class Meta:
        model = Directory
        fields = SubdirectorySerializer.Meta.fields + ['files', 'subdirectories']

    def get_files(self, obj):
        return PolymorphicSerializer(obj.files.all(), base_serializer=FileSerializer, many=True).data


class UserSerializer(serializers.ModelSerializer):
    firstName = ReadOnlyField(source="first_name")
    lastName = ReadOnlyField(source="last_name")

    class Meta:
        model = User
        fields = ('id', 'username', 'firstName', 'lastName')
