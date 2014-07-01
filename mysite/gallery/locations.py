# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import os

COLLECTION_PHYS_ROOT = '/home/przemas/Desktop/images'
STATIC_PHYS_ROOT = '/home/przemas/Desktop/homesite'

TRASH_DIRECTORY = 'Trash'

THUMBNAILS_WEB_ROOT = 'static/images/x200'
PREVIEW_WEB_ROOT = 'static/images/x1280'
THUMBNAILS_PHYS_ROOT = os.path.join(STATIC_PHYS_ROOT, THUMBNAILS_WEB_ROOT)
PREVIEW_PHYS_ROOT = os.path.join(STATIC_PHYS_ROOT, PREVIEW_WEB_ROOT)

def normpath_join(*path):
    return os.path.normpath(os.path.join(*path))

def collection_phys_path(path):
    return normpath_join(COLLECTION_PHYS_ROOT, path)

def thumbnail_web_path(path):
    return normpath_join(THUMBNAILS_WEB_ROOT, path)

def thumbnail_phys_path(path):
    return normpath_join(THUMBNAILS_PHYS_ROOT, path)

def preview_web_path(path):
    return normpath_join(PREVIEW_WEB_ROOT, path)

def preview_phys_path(path):
    return normpath_join(PREVIEW_PHYS_ROOT, path)