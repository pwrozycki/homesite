#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import re
import logging
from collections import defaultdict

from common.collectionutils.renameutils import move_without_overwriting
from common.collectionutils.exiftool import ImageInfo, JsonUtil
from common.collectionutils.pidfile import handle_pidfile
from gallery.locations import COLLECTION_PHYS_ROOT


IMG_RE = re.compile(r'^(?i).*\.(cr2|nef|jpg|xmp)$')
CORRECT_FILENAME_RE = re.compile(r'^\d{8}_\d{6}(_\d+)?\.\w{3}$')

META_ROOT = os.path.join(COLLECTION_PHYS_ROOT, '.meta')
PID_FILE = os.path.join(META_ROOT, "renamer.pid")
LOG_FILE = os.path.join(META_ROOT, "renamer.log")


class Renamer:
    def _collect_groups(self, root, images):
        self._image_groups = defaultdict(list)
        for name, image in [(os.path.splitext(x)[0], x) for x in images]:
            self._image_groups[name].append(os.path.abspath(os.path.join(root, image)))

    def _rename_groups(self):
        for name, paths in self._image_groups.items():
            self._rename_group(paths)

    @staticmethod
    def _rename_group(paths):
        image_infos = [ImageInfo.create_from_json(x) for x in JsonUtil.read_exiftool_json(paths)]
        dates = [x.date for x in image_infos]

        if len(set(dates)) > 1:
            logging.warning("different dates: {}".format(paths))
            return

        if dates[0] is None:
            logging.error("no date info: skipping: {}".format(','.join(paths)))
            return

        files_in_directory = os.listdir(os.path.dirname(paths[0]))

        for nextSuffix in range(1, 10):
            new_name = os.path.splitext(image_infos[0].new_filename)[0]
            if [x for x in files_in_directory if x.startswith(new_name)]:
                image_infos[0].suffix = str(nextSuffix)
            else:
                good_suffix = image_infos[0].suffix
                for image_info in image_infos:
                    image_info.suffix = good_suffix
                    logging.info("renaming: {0.path} -> {0.new_path}".format(image_info))
                    move_without_overwriting(image_info.path, image_info.new_path)
                return

        logging.error("too many copies, skipping rolling suffixes: {}".format(','.join(paths)))

    def walk(self):
        for (root, dirs, files) in os.walk(COLLECTION_PHYS_ROOT):
            dirs[:] = [x for x in dirs if not x.startswith('.')]
            dirs.sort()
            images = []
            for name in sorted(files):
                if CORRECT_FILENAME_RE.match(name):
                    logging.debug("correct filename, skipping: {}".format(os.path.abspath(os.path.join(root, name))))
                    continue

                if IMG_RE.match(name):
                    images.append(name)

            if not images:
                continue

            self._collect_groups(root, images)
            self._rename_groups()


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s (%(levelname)s): %(message)s", filename=LOG_FILE, level=logging.INFO)
    handle_pidfile(PID_FILE)
    Renamer().walk()