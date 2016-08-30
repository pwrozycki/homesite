import os

from django.db import models
from typedmodels.models import TypedModel


class ImageGroup(models.Model):
    time_string = models.CharField(max_length=15, unique=True, null=True)

    class Meta:
        ordering = ('time_string',)


class Directory(models.Model):
    shared = models.BooleanField(default=False)
    path = models.CharField(max_length=255, unique=True, db_index=True)
    modification_time = models.DateTimeField(null=True)
    parent = models.ForeignKey('self', related_name='subdirectories', null=True, db_index=True)

    class Meta:
        ordering = ('path',)


class File(TypedModel):
    name = models.CharField(max_length=100, db_index=True)
    directory = models.ForeignKey(Directory, related_name='%(class)ss', db_index=True)
    modification_time = models.DateTimeField(null=True)
    trash_time = models.DateTimeField(null=True)

    @property
    def path(self):
        return os.path.join(self.directory.path, self.name)

    class Meta:
        unique_together = ('name', 'directory')
        ordering = ('name',)
        # abstract = True


class Image(File):
    raw_filename = models.CharField(max_length=100, blank=True)
    orientation = models.CharField(max_length=10, blank=True, default="up")
    aspect_ratio = models.FloatField()
    image_group = models.ForeignKey(ImageGroup, related_name='images', null=True, db_index=True)


class Video(File):
    substitute_original = models.NullBooleanField(default=False)