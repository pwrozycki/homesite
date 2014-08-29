#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
import fnmatch
import logging
import subprocess
import sys

from gallery.locations import COLLECTION_PHYS_ROOT, PREVIEW_PHYS_ROOT, THUMBNAILS_PHYS_ROOT

CONFIGURATION = (
    (THUMBNAILS_PHYS_ROOT, 'x200', '-thumbnail'),
    (PREVIEW_PHYS_ROOT, 'x1280', '-resize'),
)

logger = logging.getLogger(__name__)


class Thumbnailer:
    JPG_MATCH = re.compile(fnmatch.translate('*.JPG'), re.IGNORECASE)

    @staticmethod
    def _change_path_root(path, prev_root, new_root):
        path = os.path.normpath(path)
        prev_root = os.path.normpath(prev_root)
        new_root = os.path.normpath(new_root)
        if not path.startswith(prev_root):
            logger.critical("terminating: path should be rooted in: {}".format(prev_root))
            sys.exit(-1)
        return re.sub('^' + prev_root, new_root, path)

    @classmethod
    def _dst_path(cls, path, thumbs_root):
        return cls._change_path_root(path, COLLECTION_PHYS_ROOT, thumbs_root)

    @classmethod
    def _src_path(cls, path, thumbs_root):
        return cls._change_path_root(path, thumbs_root, COLLECTION_PHYS_ROOT)

    @classmethod
    def _create_missing_dst_dir(cls, directory, dst_root):
        dst_dir = cls._dst_path(directory, dst_root)
        if not os.path.exists(dst_dir):
            logger.info("creating directory: {}".format(dst_dir))
            os.makedirs(dst_dir)

    @classmethod
    def _create_miniature(cls, image, dst_root, geometry, mode):
        dst_file = cls._dst_path(image, dst_root)

        # if thumbnail exists and is up-to-date nothing should be done
        if os.path.exists(dst_file):
            if os.path.getmtime(image) <= os.path.getmtime(dst_file):
                logger.debug("skipping (up to date image exists): {}".format(dst_file))
                return

        logger.info("creating image: {}".format(dst_file))
        subprocess.call(['convert', image, mode, geometry, '-quality', '80', dst_file])

    @classmethod
    def prepare_phase_hook(cls, root, dirs, files):
        # for each file in collection create thumbnails or preview images
        for (thumbs_root, geometry, mode) in CONFIGURATION:

            # create destination directory if missing
            for directory in dirs:
                abspath = os.path.abspath(os.path.join(root, directory))
                cls._create_missing_dst_dir(abspath, thumbs_root)

            # create thumb / resized
            for name in [f for f in sorted(files) if cls.JPG_MATCH.match(f)]:
                abspath = os.path.abspath(os.path.join(root, name))
                cls._create_miniature(abspath, thumbs_root, geometry, mode)

    @classmethod
    def _remove_file_not_in_collection(cls, dst_file, thumbs_root):
        src_file = cls._src_path(dst_file, thumbs_root)
        if not os.path.exists(src_file):
            logger.info("removing file: {}".format(dst_file))
            os.unlink(dst_file)

    @classmethod
    def _remove_dir_not_in_collection(cls, dst_dir, thumbs_root):
        src_dir = cls._src_path(dst_dir, thumbs_root)
        if not os.path.exists(src_dir):
            logger.info("removing directory: {}".format(dst_dir))
            try:
                os.rmdir(dst_dir)
            except OSError as e:
                logger.error("couldn't remove directory (not empty): " + dst_dir)

    @classmethod
    def remove_obsolete(cls):
        for (thumbs_root, geometry, mode) in CONFIGURATION:
            for (root, dirs, files) in os.walk(thumbs_root, topdown=False):
                dirs.sort()

                # remove files if no corresponding file was found
                for name in [f for f in sorted(files) if cls.JPG_MATCH.match(f)]:
                    dst_file = os.path.abspath(os.path.join(root, name))
                    cls._remove_file_not_in_collection(dst_file, thumbs_root)

                # remove directories if no corresponding dir was found
                for directory in dirs:
                    dst_dir = os.path.abspath(os.path.join(root, directory))
                    cls._remove_dir_not_in_collection(dst_dir, thumbs_root)