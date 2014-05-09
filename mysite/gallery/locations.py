#!usr/bin/env python
# -*- coding: UTF-8 -*-

import os

COLLECTION_ROOT = u'/mnt/dysk/01_ZDJĘCIA/'
THUMBNAILS_WEBROOT = u'/static/images/x200/'
COMPRESSED_WEBROOT = u'/static/images/x1280/'


def collection_path(path):
    return os.path.join(COLLECTION_ROOT, path)


def thumbnail_path(path):
    return os.path.join(THUMBNAILS_WEBROOT, path)


def image_path(path):
    return os.path.join(COMPRESSED_WEBROOT, path)