#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import logging
import re
import shutil
import subprocess
import sys

from common.collectionutils.misc import is_jpeg, is_video
from common.collectionutils.renamer import Renamer
from common.collectionutils.renameutils import get_mtime_datetime
from gallery import locations
from gallery.locations import COLLECTION_PHYS_ROOT, PREVIEW_PHYS_ROOT, THUMBNAILS_PHYS_ROOT, VIDEOS_PHYS_ROOT
from gallery.models import File


class SuffixNamingMixin:
    def get_suffix(self):
        return ''

    def name_miniature_to_original(self, f):
        return re.sub(r'{}$'.format(re.escape(self.get_suffix())), '', f, flags=re.IGNORECASE)

    def name_original_to_miniature(self, f):
        return f + self.get_suffix()


class VideoGenerator(SuffixNamingMixin):
    @staticmethod
    def will_output_file(f):
        return is_video(f)

    def get_suffix(self):
        return '.mp4'

    @staticmethod
    def miniatures_root():
        return VIDEOS_PHYS_ROOT

    def generate_miniature(self, input_path, output_path):
        with open(os.devnull, 'w') as null:
            logger.info("creating video: {}".format(output_path))
            splitext = os.path.splitext(output_path)
            tmp_output_path = splitext[0] + "_tmp" + splitext[1]
            subprocess.call(['ffmpeg', '-i', input_path, '-c:v', 'libx264', '-crf', '22', '-pix_fmt', 
                            'yuv420p', '-y', tmp_output_path], stdout=null, stderr=null)
            os.rename(tmp_output_path, output_path)


class FirstFrameGenerator(VideoGenerator):
    def get_suffix(self):
        return '.jpg'

    def generate_miniature(self, input_path, output_path):
        with open(os.devnull, 'w') as null:
            logger.info("creating video shot: {}".format(output_path))
            # scale to 320x240 but keep aspect ratio (fit in box)
            subprocess.call(['ffmpeg', '-i', input_path, '-vf', 'scale=iw*min(320/iw\,240/ih):ih*min(320/iw\,240/ih)',
                             '-vframes', '1', '-f', 'image2', '-y', output_path], stdout=null, stderr=null)


class ThumbnailGenerator(SuffixNamingMixin):
    def __init__(self, mode, geometry, miniatures_root):
        self._mode = mode
        self._geometry = geometry
        self._miniatures_root = miniatures_root

    @staticmethod
    def will_output_file(f):
        return is_jpeg(f) and Renamer.CORRECT_FILENAME_RE.match(f)

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
    def _modify_basename(path, func):
        dir_name, file_name = os.path.split(path)
        new_name = func(file_name)
        return os.path.join(dir_name, new_name)

    @classmethod
    def _miniature_phys_path(cls, collection_phys_path, generator, modify_basename=True):
        new_path = collection_phys_path
        if modify_basename:
            new_path = cls._modify_basename(new_path, generator.name_original_to_miniature)

        return cls._change_path_root(COLLECTION_PHYS_ROOT, generator.miniatures_root(), new_path)

    @classmethod
    def _collection_phys_path(cls, miniature_phys_path, generator, modify_basename=True):
        new_path = miniature_phys_path
        if modify_basename:
            new_path = cls._modify_basename(new_path, generator.name_miniature_to_original)

        return cls._change_path_root(generator.miniatures_root(), COLLECTION_PHYS_ROOT, new_path)

    @classmethod
    def _create_missing_dst_dir(cls, dir_phys_path):
        for generator in MINIATURE_GENERATORS:
            dst_dir = cls._miniature_phys_path(dir_phys_path, generator, modify_basename=False)
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

            miniature_phys_path = cls._miniature_phys_path(original_phys_path, generator)

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
            same_original_miniature_phys_path = cls._miniature_phys_path(same_original_phys_path, generator)
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
        cls._process_directory(root, dirs, files)

    @classmethod
    def _process_directory(cls, root, dirs, files):
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
    def _remove_file_not_in_collection(cls, miniature_phys_path, generator):
        # if file doesn't end in specified suffix it wasn't generated by specific generator
        # and shouldn't be deleted now
        if not re.search('{}$'.format(generator.get_suffix()), miniature_phys_path):
            return

        collection_phys_path = cls._collection_phys_path(miniature_phys_path, generator)
        if not os.path.exists(collection_phys_path):
            logger.info("removing file: {}".format(miniature_phys_path))
            os.unlink(miniature_phys_path)

    @classmethod
    def _remove_dir_not_in_collection(cls, miniatures_dir_phys_path, generator):
        collection_phys_path = cls._collection_phys_path(miniatures_dir_phys_path, generator, modify_basename=False)
        if not os.path.exists(collection_phys_path):
            logger.info("removing directory: {}".format(miniatures_dir_phys_path))
            try:
                os.rmdir(miniatures_dir_phys_path)
            except OSError as e:
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
                    cls._remove_file_not_in_collection(miniature_phys_path, generator)

                # remove directories if no corresponding dir was found
                for directory in dirs:
                    miniatures_dir_phys_path = os.path.abspath(os.path.join(root, directory))
                    cls._remove_dir_not_in_collection(miniatures_dir_phys_path, generator)
