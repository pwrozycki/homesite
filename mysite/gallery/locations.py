# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import os

COLLECTION_ROOT = '/home/przemas/Desktop/images'
STATIC_ROOT = '/home/przemas/Desktop/homesite/static'

THUMBNAILS_WEBROOT = '/static/images/x200/'
COMPRESSED_WEBROOT = '/static/images/x1280/'


def collection_path(path):
    return os.path.join(COLLECTION_ROOT, path)


def thumbnail_path(path):
    return os.path.join(THUMBNAILS_WEBROOT, path)


def image_path(path):
    return os.path.join(COMPRESSED_WEBROOT, path)