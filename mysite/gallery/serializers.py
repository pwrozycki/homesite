from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import Field
from rest_framework.relations import PrimaryKeyRelatedField
from gallery import locations

from gallery.models import Image, Directory


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
