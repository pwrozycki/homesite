# Create your models here.
from django.db.models.base import Model
from django.db import models


class Image(Model):
    path = models.CharField(max_length=1024)
    rotation = models.CharField(max_length=10) # UP | DOWN | LEFT | RIGHT