#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import os
import re
import shutil
from datetime import datetime

from django.utils import timezone

from common.collectionutils.generators import TIMESTAMP_FORMAT, TIMESTAMP_PATTERN, MINIATURE_GENERATORS
from common.collectionutils.renameutils import get_mtime_datetime
from gallery import locations
from gallery.models import File

logger = logging.getLogger(__name__)


class Thumbnailer:
    """
    Goes through collection of images/videos and creates corresponding directories for storing miniatures.
    Keeps them in sync when new files are added or old ones are removed.
    """

    @classmethod
    def _create_missing_dst_dir(cls, dir_phys_path):
        for generator in MINIATURE_GENERATORS:
            dst_dir = generator.miniature_phys_path(dir_phys_path, is_directory=True)
            if not os.path.exists(dst_dir):
                logger.info("creating directory: {}".format(dst_dir))
                os.makedirs(dst_dir)

    @classmethod
    def _create_miniature(cls, original_phys_path, miniature_phys_path, generator):
        generator.generate_miniature(original_phys_path, miniature_phys_path)

    @classmethod
    def create_miniatures(cls, original_phys_path, force_recreate=False):
        """
        For each file in collection create missing miniatures.
        Possibly move miniatures if original file has been moved.
        Recreate ones that are outdated.
        """
        for generator in MINIATURE_GENERATORS:
            # check if generator will output file for this input
            if not generator.will_output_file(os.path.basename(original_phys_path)):
                continue

            miniature_phys_path = generator.miniature_phys_path(original_phys_path)

            # recreate requested
            if force_recreate:
                cls._create_miniature(original_phys_path, miniature_phys_path, generator)

            # creation of miniature should be skipped if on of following is true:
            # - miniature exists and is up-to-date => nothing should be done
            # - miniature is symbolic link pointing back to original
            elif os.path.exists(miniature_phys_path):
                if (os.path.getmtime(original_phys_path) <= os.path.getmtime(miniature_phys_path) or
                        cls._miniature_links_back_to_original(original_phys_path, miniature_phys_path)):
                    logger.debug("skipping (up to date miniature exists): {}".format(miniature_phys_path))
                    continue

            # miniature doesn't exist
            else:
                # try to find miniature matching name and mtime
                copied = cls._try_copying_existing_miniature(original_phys_path, miniature_phys_path, generator)

                # no existing miniature for such original exists - create one
                if not copied:
                    cls._create_miniature(original_phys_path, miniature_phys_path, generator)

    @staticmethod
    def _miniature_links_back_to_original(original_phys_path, miniature_phys_path):
        islink = os.path.islink(miniature_phys_path)
        miniature_points_to_original = os.path.realpath(miniature_phys_path) == original_phys_path
        return islink and miniature_points_to_original

    @classmethod
    def _try_copying_existing_miniature(cls, original_phys_path, miniature_phys_path, generator):
        """
        When original in collection is moved to new directory, copy existing miniature instead of creating a new one.
        """
        original_mtime = get_mtime_datetime(original_phys_path)
        original_basename = os.path.basename(original_phys_path)

        # originals with same basename and modification time are considered as identical
        # therefore if there exists thumbnail it can be used instead of creating new one
        same_original_query = File.objects.filter(name=original_basename, modification_time=original_mtime)

        for same_original in same_original_query.all():
            same_original_phys_path = locations.collection_phys_path(same_original.path)

            same_original_miniature_phys_path = generator.miniature_phys_path(same_original_phys_path)
            copy_args = (same_original_miniature_phys_path, miniature_phys_path)

            # underlying thumbnail exists - thumbnails can be copied
            if os.path.exists(same_original_miniature_phys_path):
                logger.info(
                    "there exists already original with same name and mtime: copying {} -> {}".format(*copy_args))
                shutil.copy(*copy_args)
                return True

        # there was no thumbnail yet
        # this could happen when two exact copies are added and no thumbnail was created for any of them
        return False

    @classmethod
    def synchronize_miniatures_with_collection(cls, root, dirs, files):
        """
        Process directory.
        Go through collection directories and create corresponding thumbnails directories.
        Then create thumbnails for every original in collection.
        """
        # create destination directory if missing
        for directory in dirs:
            dir_phys_path = os.path.abspath(os.path.join(root, directory))
            cls._create_missing_dst_dir(dir_phys_path)

        # create miniatures
        for name in sorted(files):
            original_phys_path = os.path.abspath(os.path.join(root, name))
            cls.create_miniatures(original_phys_path)

    @classmethod
    def _remove_outdated_miniatures(cls, miniature_phys_path, generator):
        # if file doesn't end in specified suffix it wasn't generated by specific generator
        # and shouldn't be deleted in context of different generator
        if not miniature_phys_path.endswith(generator.extension()):
            return

        # if image has been removed or modified existing miniatures are outdated and should be removed
        collection_phys_path = generator.collection_phys_path(miniature_phys_path)
        if not os.path.exists(collection_phys_path) or cls._timestamps_differ(collection_phys_path,
                                                                              miniature_phys_path):
            logger.info("removing file: {}".format(miniature_phys_path))
            os.unlink(miniature_phys_path)

    @classmethod
    def _timestamps_differ(cls, collection_phys_path, miniature_phys_path):
        originals_mtime = get_mtime_datetime(collection_phys_path).replace(microsecond=0)
        miniature_mtime = cls._get_miniature_timestamp(miniature_phys_path)
        timestamps_differ = miniature_mtime != originals_mtime
        return timestamps_differ

    @classmethod
    def _get_miniature_timestamp(cls, miniature_phys_path):
        timestamp_match = re.search(TIMESTAMP_PATTERN, miniature_phys_path)
        if timestamp_match:
            timestamp_strig = timestamp_match.group(0)[1:]
            miniature_mtime = datetime.strptime(timestamp_strig, TIMESTAMP_FORMAT)
            return timezone.get_default_timezone().localize(miniature_mtime)

        return None

    @classmethod
    def _remove_dir_not_in_collection(cls, miniatures_dir_phys_path, generator):
        collection_phys_path = generator.collection_phys_path(miniatures_dir_phys_path, is_directory=True)
        if not os.path.exists(collection_phys_path):
            logger.info("removing directory: {}".format(miniatures_dir_phys_path))
            try:
                os.rmdir(miniatures_dir_phys_path)
            except OSError:
                logger.error("couldn't remove directory (not empty): " + miniatures_dir_phys_path)

    @classmethod
    def remove_obsolete(cls):
        """
        Remove thumbnails if corresponding image in collection has been removed.
        Also remove empty directories in thumbnails tree.
        """
        for generator in MINIATURE_GENERATORS:
            miniatures_root = generator.miniatures_root()

            for root, dirs, files in os.walk(miniatures_root, topdown=False):
                dirs.sort()

                # remove files if no corresponding file was found
                for name in sorted(files):
                    miniature_phys_path = os.path.abspath(os.path.join(root, name))
                    cls._remove_outdated_miniatures(miniature_phys_path, generator)

                # remove directories if no corresponding dir was found
                for directory in dirs:
                    miniatures_dir_phys_path = os.path.abspath(os.path.join(root, directory))
                    cls._remove_dir_not_in_collection(miniatures_dir_phys_path, generator)
