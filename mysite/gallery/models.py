import os

from django.db import models


class ImageGroup(models.Model):
    time_string = models.CharField(max_length=15, unique=True, null=True)

    class Meta:
        ordering = ('time_string',)


class Directory(models.Model):
    shared = models.BooleanField(default=False)
    path = models.CharField(max_length=1000, unique=True, db_index=True)
    modification_time = models.DateTimeField(null=True)
    parent = models.ForeignKey('self', related_name='subdirectories', null=True, db_index=True)

    class Meta:
        ordering = ('path',)


class Image(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    orientation = models.CharField(max_length=10, blank=True, default="up")
    directory = models.ForeignKey(Directory, related_name='images', db_index=True)
    image_group = models.ForeignKey(ImageGroup, related_name='images', null=True, db_index=True)
    modification_time = models.DateTimeField(null=True)
    trash_time = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('name', 'directory')
        ordering = ('name',)

    @property
    def path(self):
        return os.path.join(self.directory.path, self.name)
