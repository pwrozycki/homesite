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
        """
        Group images based on their non-extension part.
        """
        image_groups = defaultdict(list)
        for prefix, filename in [(os.path.splitext(x)[0], x) for x in images]:
            image_groups[prefix].append(os.path.abspath(os.path.join(root, filename)))

        return image_groups

    @classmethod
    def _rename_groups(cls, image_groups, files_in_directory):
        for key in sorted(image_groups.keys()):
            paths_in_group = image_groups[key]
            cls._try_rename_group(paths_in_group, files_in_directory)

    @classmethod
    def _rename_group(cls, image_infos, good_suffix, files_in_directory):
        """
        Change file names in image_infos list, by concatenating new suffix.
        """
        for image_info in image_infos:
            image_info.suffix = good_suffix

            logger.info("renaming: {0.path} -> {0.new_path}".format(image_info))

            # rename file
            move_without_overwriting(image_info.path, image_info.new_path)

            # remove old name, add now name to list of files
            files_in_directory.remove(os.path.basename(image_info.path))
            files_in_directory.append(os.path.basename(image_info.new_path))

    @classmethod
    def _try_rename_group(cls, group_paths, files_in_directory):
        """
        Find new non colliding name and rename files in group.
        """
        image_infos = [ImageInfo.for_path(path) for path in group_paths]
        any_info = image_infos[0]

        # check if files in group have same dates
        if cls._check_invalid_dates(group_paths, image_infos):
            return

        # try new names for group (by concatenating consecutive numbers)
        for nextSuffix in range(1, 10):
            new_prefix = os.path.splitext(any_info.new_filename)[0]


            # skip this loop if collision detected
            collision_detected = bool([x for x in files_in_directory if x.startswith(new_prefix)])
            if collision_detected:
                any_info.suffix = str(nextSuffix)
                continue

            # rename if no collision detected
            non_colliding_suffix = any_info.suffix
            cls._rename_group(image_infos, non_colliding_suffix, files_in_directory)
            return

        logger.error("too many copies, skipping rolling suffixes: {}".format(','.join(group_paths)))

    @staticmethod
    def _check_invalid_dates(group_paths, image_infos):
        """
        Renaming is possible, when every file in group has same date information.
        Otherwise it is impossible to select unambiguous name.
        """
        differing_or_missing_dates = False

        dates = [x.date for x in image_infos]
        if len(set(dates)) > 1:
            logger.warning("different dates: {}".format(group_paths))
            differing_or_missing_dates = True

        if dates[0] is None:
            logger.error("no date info: skipping: {}".format(','.join(group_paths)))
            differing_or_missing_dates = True

        return differing_or_missing_dates

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