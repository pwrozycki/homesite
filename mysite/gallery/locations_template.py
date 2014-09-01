# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import os
import re

STATIC_URL = '/static'

COLLECTION_PHYS_ROOT = '%COLLECTION_PHYS_ROOT%'
STATIC_PHYS_ROOT = '%STATIC_PHYS_ROOT%'

TRASH_DIR_NAME = 'Trash'
THUMBNAILS_DIR_NAME = 'x200'
PREVIEW_DIR_NAME = 'x1280'

THUMBNAILS_PHYS_ROOT = os.path.join(STATIC_PHYS_ROOT, THUMBNAILS_DIR_NAME)
PREVIEW_PHYS_ROOT = os.path.join(STATIC_PHYS_ROOT, PREVIEW_DIR_NAME)


def normpath_join(*path):
    return os.path.normpath(os.path.join(*path))


def collection_web_path(phys_path):
    norm_phys_path = os.path.normpath(phys_path)
    if not norm_phys_path.startswith(COLLECTION_PHYS_ROOT):
        raise Exception("Incorrect filename")

    return re.sub('^' + COLLECTION_PHYS_ROOT + '/?', '', norm_phys_path)


def thumbnail_web_path(web_path):
    return normpath_join(STATIC_URL, THUMBNAILS_DIR_NAME, web_path)


def preview_web_path(web_path):
    return normpath_join(STATIC_URL, PREVIEW_DIR_NAME, web_path)


def collection_phys_path(web_path):
    return normpath_join(COLLECTION_PHYS_ROOT, web_path)


def thumbnail_phys_path(web_path):
    return normpath_join(THUMBNAILS_PHYS_ROOT, web_path)


def preview_phys_path(web_path):
    return normpath_join(PREVIEW_PHYS_ROOT, web_path)


def collection_walk():
    for (root, dirs, files) in os.walk(COLLECTION_PHYS_ROOT):
        dirs[:] = [x for x in dirs if not x.startswith('.')]
        dirs.sort()
        files.sort()
        yield (root, dirs, files)