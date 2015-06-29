from contextlib import suppress

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField

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

    def get_path(self, obj):
        return getattr(obj, 'path')

    def get_type(self, obj):
        return obj.type.split('.')[-1]

    class Meta:
        fields = ['id', 'path', 'type']


class ImageSerializer(FileSerializer):
    class Meta:
        model = Image
        fields = FileSerializer.Meta.fields + ['orientation', 'aspect_ratio']


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
        return get_polymorphic_serializer(FileSerializer)(obj.files.all(), many=True).data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')
