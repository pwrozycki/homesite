# Create your models here.
from django.db import models


class Directory(models.Model):
    path = models.CharField(max_length=1000, unique=True)
    parent = models.ForeignKey('self', related_name='directories', null=True)
    thumbnail_path = models.CharField(max_length=1000)
    preview_path = models.CharField(max_length=1000)


class Image(models.Model):
    name = models.CharField(max_length=100)
    orientation = models.CharField(max_length=10)
    directory = models.ForeignKey(Directory, related_name='images')