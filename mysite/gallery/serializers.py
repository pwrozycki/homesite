from rest_framework import serializers
from gallery.models import Image, Directory


class DirectorySerializer(serializers.ModelSerializer):
    images = serializers.PrimaryKeyRelatedField(many=True)
    directories = serializers.PrimaryKeyRelatedField(many=True)
    class Meta:
        model = Directory
        fields = ['path', 'thumbnail_path', 'preview_path', 'images', 'parent', 'directories']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['name', 'directory', 'orientation']