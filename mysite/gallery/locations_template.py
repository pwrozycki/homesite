# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import os
import re

COLLECTION_PHYS_ROOT = '%COLLECTION_PHYS_ROOT%'
STATIC_PHYS_ROOT = '%STATIC_PHYS_ROOT%'

TRASH_DIRECTORY = 'Trash'
THUMBNAILS_WEB_ROOT = 'static/images/x200'
PREVIEW_WEB_ROOT = 'static/images/x1280'

THUMBNAILS_PHYS_ROOT = os.path.join(STATIC_PHYS_ROOT, THUMBNAILS_WEB_ROOT)
PREVIEW_PHYS_ROOT = os.path.join(STATIC_PHYS_ROOT, PREVIEW_WEB_ROOT)


def normpath_join(*path):
    return os.path.normpath(os.path.join(*path))


def collection_web_path(phys_path):
    norm_phys_path = os.path.normpath(phys_path)
    if not norm_phys_path.startswith(COLLECTION_PHYS_ROOT):
        raise Exception("Incorrect filename")

    return re.sub('^' + COLLECTION_PHYS_ROOT + '/?', '', norm_phys_path)


def thumbnail_web_path(path):
    return normpath_join('/', THUMBNAILS_WEB_ROOT, path)


def preview_web_path(path):
    return normpath_join('/', PREVIEW_WEB_ROOT, path)


def collection_phys_path(path):
    return normpath_join(COLLECTION_PHYS_ROOT, path)


def thumbnail_phys_path(path):
    return normpath_join(THUMBNAILS_PHYS_ROOT, path)


def preview_phys_path(path):
    return normpath_join(PREVIEW_PHYS_ROOT, path)
