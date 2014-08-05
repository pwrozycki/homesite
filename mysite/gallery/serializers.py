from rest_framework import serializers

from gallery.models import Image, Directory


class SubdirectorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = Directory
        fields = ['id', 'path', 'thumbnail_path', 'preview_path', 'parent']


class ImageSerializer(serializers.ModelSerializer):
    directory = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = Image
        fields = ['id', 'name', 'orientation', 'directory']


class DirectorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField()
    images = ImageSerializer(many=True)
    subdirectories = SubdirectorySerializer(many=True)

    class Meta:
        model = Directory
        fields = ['id', 'path', 'thumbnail_path', 'preview_path', 'parent', 'images', 'subdirectories']
