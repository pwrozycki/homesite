#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
import logging
from collections import defaultdict

from gallery.locations import collection_walk
from common.collectionutils.renameutils import move_without_overwriting
from common.collectionutils.exiftool import ImageInfo


logger = logging.getLogger(__name__)


class Renamer:
    """
    Renames images based on creation date. Creation date is derived from exif information stored in JPG images -
    namely DateTimeOriginal and DateTime exif fields. If exif metadata is missing file modification time is used.
    Renamer processes groups of images differing only by their extension - NEF, CR2, JPG, XMP files will be renamed too.
    """
    IMG_RE = re.compile(r'^(?i).*\.(cr2|nef|jpg|xmp)$')
    CORRECT_FILENAME_RE = re.compile(r'^\d{8}_\d{6}(_\d+)?\.\w{3}$')

    @staticmethod
    def _collect_groups(root, images):
        image_groups = defaultdict(list)
        for name, image in [(os.path.splitext(x)[0], x) for x in images]:
            image_groups[name].append(os.path.abspath(os.path.join(root, image)))
        return image_groups

    @classmethod
    def _rename_groups(cls, image_groups, files):
        for key in sorted(image_groups.keys()):
            paths = image_groups[key]
            cls._rename_group(paths, files)

    @staticmethod
    def _rename_group(paths, files):
        image_infos = [ImageInfo.for_path(path) for path in paths]
        dates = [x.date for x in image_infos]

        if len(set(dates)) > 1:
            logger.warning("different dates: {}".format(paths))
            return

        if dates[0] is None:
            logger.error("no date info: skipping: {}".format(','.join(paths)))
            return

        for nextSuffix in range(1, 10):
            new_name = os.path.splitext(image_infos[0].new_filename)[0]
            if [x for x in files if x.startswith(new_name)]:
                image_infos[0].suffix = str(nextSuffix)
            else:
                good_suffix = image_infos[0].suffix
                for image_info in image_infos:
                    image_info.suffix = good_suffix
                    logger.info("renaming: {0.path} -> {0.new_path}".format(image_info))
                    move_without_overwriting(image_info.path, image_info.new_path)
                    files[files.index(os.path.basename(image_info.path))] = os.path.basename(image_info.new_path)

                return

        logger.error("too many copies, skipping rolling suffixes: {}".format(','.join(paths)))

    @classmethod
    def walk(cls):
        for (root, dirs, files) in collection_walk():
            cls._process_directory(root, dirs, files)

    @classmethod
    def _process_directory(cls, root, dirs, files):
        images = []
        for name in sorted(files):
            if cls.CORRECT_FILENAME_RE.match(name):
                logger.debug("correct filename, skipping: {}".format(os.path.abspath(os.path.join(root, name))))
                continue

            if cls.IMG_RE.match(name):
                images.append(name)

        if not images:
            return

        groups = cls._collect_groups(root, images)
        cls._rename_groups(groups, files)