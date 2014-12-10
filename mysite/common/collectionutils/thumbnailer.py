#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
import fnmatch
import logging
import shutil
import subprocess
import sys

from common.collectionutils.renameutils import get_mtime_datetime
from gallery import locations
from gallery.locations import COLLECTION_PHYS_ROOT, PREVIEW_PHYS_ROOT, THUMBNAILS_PHYS_ROOT, collection_walk
from gallery.models import Image


THUMBNAILS_CONVERT_CONF = (
    (THUMBNAILS_PHYS_ROOT, 'x200', '-thumbnail'),
    (PREVIEW_PHYS_ROOT, 'x1280', '-resize'),
)

logger = logging.getLogger(__name__)


class Thumbnailer:

    JPG_MATCH = re.compile(fnmatch.translate('*.JPG'), re.IGNORECASE)

    @staticmethod
    def _change_path_root(prev_root, new_root, path):
        path = os.path.normpath(path)
        prev_root = os.path.normpath(prev_root)
        new_root = os.path.normpath(new_root)
        if not path.startswith(prev_root):
            logger.critical("terminating: path should be rooted in: {}".format(prev_root))
            sys.exit(-1)
        return re.sub('^' + prev_root, new_root, path)

    @classmethod
    def _thumb_phys_path(cls, thumb_root, collection_phys_path):
        return cls._change_path_root(COLLECTION_PHYS_ROOT, thumb_root, collection_phys_path)

    @classmethod
    def _collection_phys_path(cls, thumb_phys_path, thumb_root):
        return cls._change_path_root(thumb_root, COLLECTION_PHYS_ROOT, thumb_phys_path)

    @classmethod
    def _create_missing_dst_dir(cls, dir_phys_path):
        for (thumb_root, geometry, mode) in THUMBNAILS_CONVERT_CONF:
            dst_dir = cls._thumb_phys_path(thumb_root, dir_phys_path)
            if not os.path.exists(dst_dir):
                logger.info("creating directory: {}".format(dst_dir))
                os.makedirs(dst_dir)

    @classmethod
    def _create_thumbnail(cls, image_phys_path, thumb_phys_path, geometry, mode):
        logger.info("creating image: {}".format(thumb_phys_path))
        subprocess.call(['convert', image_phys_path, mode, geometry, '-quality', '80', thumb_phys_path])

    @classmethod
    def create_thumbnails(cls, image_phys_path, force_recreate=False):
        for (thumb_root, geometry, mode) in THUMBNAILS_CONVERT_CONF:
            # for each file in collection create thumbnails
            thumb_phys_path = cls._thumb_phys_path(thumb_root, image_phys_path)

            # recreate requested
            if force_recreate:
                cls._create_thumbnail(image_phys_path, thumb_phys_path, geometry, mode)

            # thumbnail exists and is up-to-date => nothing should be done
            elif os.path.exists(thumb_phys_path) and not force_recreate:
                if os.path.getmtime(image_phys_path) <= os.path.getmtime(thumb_phys_path):
                    logger.debug("skipping (up to date image exists): {}".format(thumb_phys_path))
                    return

            # thumbnail doesn't exist
            else:
                # found images matching name and mtime
                thumbnail_copied = cls._try_copying_existing_thumbnail(image_phys_path, thumb_phys_path, thumb_root)

                # no existing thumbnail for such image exists - create one
                if not thumbnail_copied:
                    cls._create_thumbnail(image_phys_path, thumb_phys_path, geometry, mode)

    @classmethod
    def _try_copying_existing_thumbnail(cls, image_phys_path, thumb_phys_path, thumb_root):
        image_mtime = get_mtime_datetime(image_phys_path)
        image_basename = (os.path.basename(image_phys_path))

        # images with same basename and modification time are considered as identical
        # therefore if there exists thumbnail it can be used instead of creating new one
        same_image_query = Image.objects.filter(name=image_basename, modification_time=image_mtime)

        for same_image in same_image_query.all():
            same_image_phys_path = locations.collection_phys_path(same_image.path)
            same_image_thumb_phys_path = cls._thumb_phys_path(thumb_root, same_image_phys_path)
            move_args = (same_image_thumb_phys_path, thumb_phys_path)

            # underlying thumbnail exists - thumbnails can be copied
            if os.path.exists(same_image_thumb_phys_path):
                logger.warning(
                    "there exists already image with same name and mtime: copying {} -> {}".format(*move_args))
                shutil.copy(same_image_thumb_phys_path, thumb_phys_path)
                return True

        # there was no thumbnail yet
        # this could happen when two image exact copies are added and no thumbnail was created for any of them
        return False

    @classmethod
    def walk(cls):
        for (root, dirs, files) in collection_walk():
            cls._process_directory(root, dirs, files)

    @classmethod
    def _process_directory(cls, root, dirs, files):
        # create destination directory if missing
        for directory in dirs:
            dir_phys_path = os.path.abspath(os.path.join(root, directory))
            cls._create_missing_dst_dir(dir_phys_path)

        # create thumb / resized
        for name in [f for f in sorted(files) if cls.JPG_MATCH.match(f)]:
            image_phys_path = os.path.abspath(os.path.join(root, name))
            cls.create_thumbnails(image_phys_path)

    @classmethod
    def _remove_file_not_in_collection(cls, thumb_phys_path, thumb_root):
        collection_phys_path = cls._collection_phys_path(thumb_phys_path, thumb_root)
        if not os.path.exists(collection_phys_path):
            logger.info("removing file: {}".format(thumb_phys_path))
            os.unlink(thumb_phys_path)

    @classmethod
    def _remove_dir_not_in_collection(cls, thumb_dir_phys_path, thumb_root):
        collection_phys_path = cls._collection_phys_path(thumb_dir_phys_path, thumb_root)
        if not os.path.exists(collection_phys_path):
            logger.info("removing directory: {}".format(thumb_dir_phys_path))
            try:
                os.rmdir(thumb_dir_phys_path)
            except OSError as e:
                logger.error("couldn't remove directory (not empty): " + thumb_dir_phys_path)

    @classmethod
    def remove_obsolete(cls):
        for (thumb_root, geometry, mode) in THUMBNAILS_CONVERT_CONF:
            for (root, dirs, files) in os.walk(thumb_root, topdown=False):
                dirs.sort()

                # remove files if no corresponding file was found
                for name in [f for f in sorted(files) if cls.JPG_MATCH.match(f)]:
                    thumb_phys_path = os.path.abspath(os.path.join(root, name))
                    cls._remove_file_not_in_collection(thumb_phys_path, thumb_root)

                # remove directories if no corresponding dir was found
                for directory in dirs:
                    thumb_dir_phys_path = os.path.abspath(os.path.join(root, directory))
                    cls._remove_dir_not_in_collection(thumb_dir_phys_path, thumb_root)