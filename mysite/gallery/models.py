# Create your models here.
import os
from django.db import models


class Directory(models.Model):
    path = models.CharField(max_length=1000, unique=True, db_index=True)
    modification_time = models.DateTimeField(null=True)
    parent = models.ForeignKey('self', related_name='subdirectories', null=True, db_index=True)
    thumbnail_path = models.CharField(max_length=1000)
    preview_path = models.CharField(max_length=1000)

    class Meta:
        ordering = ('path',)


class Image(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    orientation = models.CharField(max_length=10)
    directory = models.ForeignKey(Directory, related_name='images', db_index=True)

    class Meta:
        unique_together = ('name', 'directory')
        ordering = ('name',)

    @property
    def path(self):
        return os.path.join(self.directory.path, self.name)
