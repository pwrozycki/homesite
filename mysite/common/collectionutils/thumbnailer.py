#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from abc import abstractmethod, ABCMeta
from datetime import datetime
import os
import logging
import re
import shutil
import subprocess
import sys

from common.collectionutils.misc import is_jpeg, is_video, localized_time
from common.collectionutils.renamer import Renamer
from common.collectionutils.renameutils import get_mtime_datetime
from gallery import locations
from gallery.locations import COLLECTION_PHYS_ROOT, PREVIEW_PHYS_ROOT, THUMBNAILS_PHYS_ROOT, VIDEOS_PHYS_ROOT
from gallery.models import File

TIMESTAMP_FORMAT = "%y%m%d:%H%M%S"
TIMESTAMP_PATTERN = r'_\d{6}:\d{6}'


class GeneratorBase(metaclass=ABCMeta):
    def extension(self):
        return ''

    def _name_miniature_to_original(self, f):
        pattern = TIMESTAMP_PATTERN + re.escape(self.extension()) + r'$'
        return re.sub(pattern, '', f, flags=re.IGNORECASE)

    def _name_original_to_miniature(self, f):
        timestamp = get_mtime_datetime(f).strftime(TIMESTAMP_FORMAT)
        return f + "_" + timestamp + self.extension()

    @abstractmethod
    def miniatures_root(self):
        pass

    @staticmethod
    def _change_path_root(prev_root, new_root, path):
        path = os.path.normpath(path)
        prev_root = os.path.normpath(prev_root)
        new_root = os.path.normpath(new_root)
        if not path.startswith(prev_root):
            logger.critical("terminating: path should be rooted in: {}".format(prev_root))
            sys.exit(-1)
        return re.sub('^' + prev_root, new_root, path)

    @staticmethod
    def _modify_filename(path, func):
        # Return result of function if path points to file
        if os.path.isfile(path):
            return func(path)
        # Return unchanged if path points to directory
        elif os.path.isdir(path):
            return path
        else:
            raise Exception("Path {} should point to either file or directory: ".format(path))

    def miniature_phys_path(self, collection_phys_path):
        tmp_path = self._modify_filename(collection_phys_path, self._name_original_to_miniature)
        return self._change_path_root(COLLECTION_PHYS_ROOT, self.miniatures_root(), tmp_path)

    def collection_phys_path(self, miniature_phys_path):
        tmp_path = self._modify_filename(miniature_phys_path, self._name_miniature_to_original)
        return self._change_path_root(self.miniatures_root(), COLLECTION_PHYS_ROOT, tmp_path)


class VideoGenerator(GeneratorBase):
    def will_output_file(self, f):
        return is_video(f)

    def extension(self):
        return '.mp4'

    def miniatures_root(self):
        return VIDEOS_PHYS_ROOT

    def generate_miniature(self, input_path, output_path):
        with open(os.devnull, 'w') as null:
            logger.info("creating video: {}".format(output_path))
            splitext = os.path.splitext(output_path)
            tmp_output_path = splitext[0] + "_tmp" + splitext[1]
            subprocess.call(['ffmpeg', '-i', input_path, '-c:v', 'libx264', '-crf', '22', '-pix_fmt',
                             'yuv420p', '-y', '-threads', '4', tmp_output_path], stdout=null, stderr=null)
            os.rename(tmp_output_path, output_path)


class FirstFrameGenerator(VideoGenerator):
    def extension(self):
        return '.jpg'

    def generate_miniature(self, input_path, output_path):
        with open(os.devnull, 'w') as null:
            logger.info("creating video shot: {}".format(output_path))
            # scale to 320x240 but keep aspect ratio (fit in box)
            subprocess.call(['ffmpeg', '-i', input_path, '-vf', 'scale=iw*min(320/iw\,240/ih):ih*min(320/iw\,240/ih)',
                             '-vframes', '1', '-f', 'image2', '-y', output_path], stdout=null, stderr=null)


class ThumbnailGenerator(GeneratorBase):
    def __init__(self, mode, geometry, miniatures_root):
        self._mode = mode
        self._geometry = geometry
        self._miniatures_root = miniatures_root

    def extension(self):
        return '.jpg'

    def will_output_file(self, f):
        return bool(is_jpeg(f) and Renamer.CORRECT_FILENAME_RE.match(f))

    def miniatures_root(self):
        return self._miniatures_root

    def generate_miniature(self, input_path, output_path):
        logger.info("creating image: {}".format(output_path))
        subprocess.call(['convert', input_path, self._mode, self._geometry, '-quality', '80', output_path])


MINIATURE_GENERATORS = [
    ThumbnailGenerator('-thumbnail', 'x200', THUMBNAILS_PHYS_ROOT),
    ThumbnailGenerator('-resize', 'x1280', PREVIEW_PHYS_ROOT),
    VideoGenerator(),
    FirstFrameGenerator(),
]

logger = logging.getLogger(__name__)


class Thumbnailer:
    """
    Goes through collection of images/videos and creates corresponding directories for storing miniatures.
    Keeps them in sync when new files are added or old ones are removed.
    """

    @classmethod
    def _create_missing_dst_dir(cls, dir_phys_path):
        for generator in MINIATURE_GENERATORS:
            dst_dir = generator.miniature_phys_path(dir_phys_path)
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

            # miniature exists and is up-to-date => nothing should be done
            # (process next miniature configuration)
            elif os.path.exists(miniature_phys_path):
                if os.path.getmtime(original_phys_path) <= os.path.getmtime(miniature_phys_path):
                    logger.debug("skipping (up to date miniature exists): {}".format(miniature_phys_path))
                    continue

            # miniature doesn't exist
            else:
                # try to find miniature matching name and mtime
                copied = cls._try_copying_existing_miniature(original_phys_path, miniature_phys_path, generator)

                # no existing miniature for such original exists - create one
                if not copied:
                    cls._create_miniature(original_phys_path, miniature_phys_path, generator)

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

            # without original file we cannot determine the path of miniature (originals' mtime is needed)
            if not os.path.exists(same_original_phys_path):
                continue

            same_original_miniature_phys_path = generator.miniature_phys_path(same_original_phys_path)
            copy_args = (same_original_miniature_phys_path, miniature_phys_path)

            # underlying thumbnail exists - thumbnails can be copied
            if os.path.exists(same_original_miniature_phys_path):
                logger.warning(
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
            return localized_time(miniature_mtime)

        return None

    @classmethod
    def _remove_dir_not_in_collection(cls, miniatures_dir_phys_path, generator):
        collection_phys_path = generator.collection_phys_path(miniatures_dir_phys_path)
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
