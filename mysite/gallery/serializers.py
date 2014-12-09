from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import Field

from gallery.models import Image, Directory, ImageGroup


class SubdirectorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = Directory
        fields = ['id', 'path', 'shared', 'parent']


class ImageSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField('get_path')

    class Meta:
        model = Image
        fields = ['id', 'path', 'orientation']

    def get_path(self, obj):
        return getattr(obj, 'path')


class ImageGroupSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField('get_images')

    class Meta:
        model = ImageGroup

    def get_images(self, obj):
        images_queryset = obj.images\
            .exclude(directory__path__iexact='Trash')\
            .exclude(directory__path__startswith='Trash/')
        return ImageSerializer(images_queryset, many=True).data


class DirectorySerializer(SubdirectorySerializer):
    images = ImageSerializer(many=True)
    subdirectories = SubdirectorySerializer(many=True)

    class Meta:
        model = Directory
        fields = SubdirectorySerializer.Meta.fields + ['images', 'subdirectories']


class UserSerializer(serializers.ModelSerializer):
    firstName = Field(source="first_name")
    lastName = Field(source="last_name")

    class Meta:
        model = User
        fields = ('id', 'username', 'firstName', 'lastName')
