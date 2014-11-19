from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from gallery import locations

from gallery.models import Image, Directory


class SubdirectorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField()
    thumbnail_path = serializers.SerializerMethodField('get_thumbnail_path')
    original_path = serializers.SerializerMethodField('get_original_path')
    preview_path = serializers.SerializerMethodField('get_preview_path')

    def get_thumbnail_path(self, obj):
        return locations.thumbnail_web_path(obj.path)

    def get_original_path(self, obj):
        return locations.original_web_path(obj.path)

    def get_preview_path(self, obj):
        return locations.preview_web_path(obj.path)

    class Meta:
        model = Directory
        fields = ['id', 'path', 'original_path', 'thumbnail_path', 'preview_path', 'shared', 'parent']


class ImageSerializer(serializers.ModelSerializer):
    directory = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = Image
        fields = ['id', 'name', 'orientation', 'directory']


class DirectorySerializer(SubdirectorySerializer):
    images = PrimaryKeyRelatedField(many=True)
    subdirectories = PrimaryKeyRelatedField(many=True)

    class Meta:
        model = Directory
        fields = SubdirectorySerializer.Meta.fields + ['images', 'subdirectories']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')
