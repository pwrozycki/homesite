# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import os
import re


COLLECTION_PHYS_ROOT = '/collection'

TRASH_DIR_NAME = 'Trash'
TRASH_DIRECTORY_REGEXP = r'^/?{}/'.format(TRASH_DIR_NAME)
THUMBNAILS_DIR_NAME = '.thumbnails/x200'
PREVIEW_DIR_NAME = '.thumbnails/x1280'
VIDEOS_DIR_NAME = '.videos'

THUMBNAILS_PHYS_ROOT = os.path.join(COLLECTION_PHYS_ROOT, THUMBNAILS_DIR_NAME)
PREVIEW_PHYS_ROOT = os.path.join(COLLECTION_PHYS_ROOT, PREVIEW_DIR_NAME)
VIDEOS_PHYS_ROOT = os.path.join(COLLECTION_PHYS_ROOT, VIDEOS_DIR_NAME)

COLLECTION_WEB_ROOT = '/static/collection'
THUMBNAILS_WEB_ROOT = os.path.join(COLLECTION_WEB_ROOT, THUMBNAILS_DIR_NAME)
PREVIEWS_WEB_ROOT = os.path.join(COLLECTION_WEB_ROOT, PREVIEW_DIR_NAME)
VIDEOS_WEB_ROOT = os.path.join(COLLECTION_WEB_ROOT, VIDEOS_DIR_NAME)


def normpath_join(*path):
    return os.path.normpath(os.path.join(*path))


def collection_web_path(phys_path):
    norm_phys_path = os.path.normpath(phys_path)
    if not norm_phys_path.startswith(COLLECTION_PHYS_ROOT):
        raise Exception("Incorrect filename")

    return re.sub('^' + COLLECTION_PHYS_ROOT + '/?', '', norm_phys_path)


def collection_phys_path(web_path):
    return normpath_join(COLLECTION_PHYS_ROOT, web_path)


def web_path_in_trash(web_path):
    return re.search(TRASH_DIRECTORY_REGEXP, web_path)


def collection_walk():
    for (root, dirs, files) in os.walk(COLLECTION_PHYS_ROOT):
        dirs[:] = [x for x in dirs if not x.startswith('.')]
        dirs.sort()
        files.sort()
        yield (root, dirs, files)
