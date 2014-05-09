#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import atexit
import os
import re
import fnmatch
import logging
import subprocess
import sys

from pidfile import create_pidfile

COMMON_ROOT = '/mnt/dysk/'
COLLECTION_ROOT = os.path.join(COMMON_ROOT, '01_ZDJĘCIA/')

CONFIGURATION = (
    (os.path.join(COMMON_ROOT, 'homesite/static/images/x1280/'), 'x1280', '-resize'),
    (os.path.join(COMMON_ROOT, 'homesite/static/images/x200/'), 'x200', '-thumbnail'),
)

META_ROOT = os.path.join(COLLECTION_ROOT, '.meta')
PID_FILE = os.path.join(META_ROOT, "thumbnailer.pid")
LOG_FILE = os.path.join(META_ROOT, "thumbnailer.log")


class Thumbnailer:
    JPG_MATCH = re.compile(fnmatch.translate('*.JPG'), re.IGNORECASE)

    def __init__(self):
        self._create_pid_file()

    def _create_pid_file(self):
        logging.info('creating pidfile')
        if not create_pidfile(PID_FILE):
            logging.error('pidfile exists: exiting')
            sys.exit(1)
        atexit.register(self._remove_pid_file)

    def _remove_pid_file(self):
        logging.info('removing pidfile')
        os.unlink(PID_FILE)

    @staticmethod
    def change_path_root(path, prev_root, new_root):
        if not path.startswith(prev_root):
            logging.critical("terminating: path should be rooted in: {}".format(prev_root))
            sys.exit(-1)
        return re.sub('^' + prev_root, new_root, path)

    @classmethod
    def dst_path(cls, path, thumbs_root):
        return cls.change_path_root(path, COLLECTION_ROOT, thumbs_root)

    @classmethod
    def src_path(cls, path, thumbs_root):
        return cls.change_path_root(path, thumbs_root, COLLECTION_ROOT)

    @classmethod
    def create_missing_dst_dir(cls, directory, dst_root):
        dst_dir = cls.dst_path(directory, dst_root)
        if not os.path.exists(dst_dir):
            logging.info("creating directory: {}".format(dst_dir))
            os.makedirs(dst_dir)

    @classmethod
    def create_miniature(cls, image, dst_root, geometry, mode):
        dst_file = cls.dst_path(image, dst_root)
        if os.path.exists(dst_file):
            if os.path.getmtime(image) <= os.path.getmtime(dst_file):
                logging.debug("skipping (up to date image exists): {}".format(dst_file))
                return

        logging.info("creating image: {}".format(dst_file))
        subprocess.call(['convert', image, mode, geometry, '-quality', '80', dst_file])

    @classmethod
    def create_images(cls):
        for (thumbs_root, geometry, mode) in CONFIGURATION:
            # for each file in collection create thubnails or resized files
            for (root, dirs, files) in os.walk(COLLECTION_ROOT):
                dirs = [x for x in dirs if not x.startswith('.')]
                dirs.sort(key=lambda x: x.lower())

                # create destination directory if missing
                for directory in dirs:
                    abspath = os.path.abspath(os.path.join(root, directory))
                    cls.create_missing_dst_dir(abspath, thumbs_root)

                # create thumb / resized
                for name in [f for f in sorted(files) if cls.JPG_MATCH.match(f)]:
                    abspath = os.path.abspath(os.path.join(root, name))
                    cls.create_miniature(abspath, thumbs_root, geometry, mode)

    @classmethod
    def remove_file_not_in_collection(cls, dst_file, thumbs_root):
        src_file = cls.src_path(dst_file, thumbs_root)
        if not os.path.exists(src_file):
            logging.info("removing file: {}".format(dst_file))
            os.unlink(dst_file)

    @classmethod
    def remove_dir_not_in_collection(cls, dst_dir, thumbs_root):
        src_dir = cls.src_path(dst_dir, thumbs_root)
        if not os.path.exists(src_dir):
            logging.info("removing directory: {}".format(dst_dir))
            os.rmdir(dst_dir)

    @classmethod
    def remove_obsolete(cls):
        for (thumbs_root, geometry, mode) in CONFIGURATION:
            for (root, dirs, files) in os.walk(thumbs_root):
                dirs[:] = [x for x in dirs if not x.startswith('.')]
                dirs.sort()

                # remove files if no corresponding file was found
                for name in [f for f in sorted(files) if cls.JPG_MATCH.match(f)]:
                    dst_file = os.path.abspath(os.path.join(root, name))
                    cls.remove_file_not_in_collection(dst_file, thumbs_root)

                # remove directories if no corresponding dir was found
                for directory in dirs:
                    dst_dir = os.path.abspath(os.path.join(root, directory))
                    cls.remove_dir_not_in_collection(dst_dir, thumbs_root)


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s (%(levelname)s): %(message)s", filename=LOG_FILE, level=logging.INFO)
    thumbnailer = Thumbnailer()
    thumbnailer.create_images()
    thumbnailer.remove_obsolete()