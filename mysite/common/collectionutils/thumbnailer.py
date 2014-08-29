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

from gallery.locations import COLLECTION_PHYS_ROOT, PREVIEW_PHYS_ROOT, THUMBNAILS_PHYS_ROOT
from gallery.models import Image

CONFIGURATION = (
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
    def _create_missing_dst_dir(cls, dir_phys_path, dst_root):
        dst_dir = cls._thumb_phys_path(dst_root, dir_phys_path)
        if not os.path.exists(dst_dir):
            logger.info("creating directory: {}".format(dst_dir))
            os.makedirs(dst_dir)

    @classmethod
    def _create_minified(cls, image_phys_path, thumb_root, geometry, mode):
        thumb_phys_path = cls._thumb_phys_path(thumb_root, image_phys_path)

        # if thumbnail exists and is up-to-date nothing should be done
        if os.path.exists(thumb_phys_path):
            if os.path.getmtime(image_phys_path) <= os.path.getmtime(thumb_phys_path):
                logger.debug("skipping (up to date image exists): {}".format(thumb_phys_path))
                return

        # thumbnail doesn't exist
        else:
            image_mtime = get_mtime_datetime(image_phys_path)
            image_basename = (os.path.basename(image_phys_path))
            same_image_query = Image.objects.filter(name=image_basename, modification_time=image_mtime)

            # found images matching name and mtime
            if same_image_query:
                # there are many such images - first will be taken into account - but log warning
                if len(same_image_query) > 1:
                    logger.warning("found many images with name: {} and matching mtime".format(image_basename))

                same_image = same_image_query[0]
                same_image_phys_path = locations.collection_phys_path(same_image.path)
                same_image_thumb_phys_path = cls._thumb_phys_path(thumb_root, same_image_phys_path)
                move_args = (same_image_thumb_phys_path, thumb_phys_path)

                # underlying image exists - thumbnails can be copied
                if os.path.exists(same_image_phys_path):
                    logger.warning(
                        "there exists already image with same name and mtime: copying {} -> {}".format(*move_args))
                    shutil.copy(same_image_thumb_phys_path, thumb_phys_path)

                # image has been moved - thumbnails should be moved
                else:
                    logger.info("move detected, moving {} -> {} ".format(*move_args))
                    shutil.move(*move_args)

            # no existing thumbnail for such image exists - create one
            else:
                logger.info("creating image: {}".format(thumb_phys_path))
                subprocess.call(['convert', image_phys_path, mode, geometry, '-quality', '80', thumb_phys_path])

    @classmethod
    def prepare_phase_hook(cls, root, dirs, files):
        # for each file in collection create thumbnails or preview images
        for (thumb_root, geometry, mode) in CONFIGURATION:

            # create destination directory if missing
            for directory in dirs:
                dir_phys_path = os.path.abspath(os.path.join(root, directory))
                cls._create_missing_dst_dir(dir_phys_path, thumb_root)

            # create thumb / resized
            for name in [f for f in sorted(files) if cls.JPG_MATCH.match(f)]:
                image_phys_path = os.path.abspath(os.path.join(root, name))
                cls._create_minified(image_phys_path, thumb_root, geometry, mode)

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
        for (thumb_root, geometry, mode) in CONFIGURATION:
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