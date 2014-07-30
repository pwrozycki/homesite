from rest_framework import serializers
from gallery.models import Image, Directory


class DirectorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField()
    images = serializers.PrimaryKeyRelatedField(many=True)
    directories = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = Directory
        fields = ['id', 'path', 'thumbnail_path', 'preview_path', 'parent', 'images', 'directories']


class ImageSerializer(serializers.ModelSerializer):
    directory = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = Image
        fields = ['id', 'name', 'orientation', 'directory']
