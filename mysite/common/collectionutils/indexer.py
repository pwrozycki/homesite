import datetime
import logging
import os
from common.collectionutils.pidfile import _create_pidfile, handle_pidfile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import re
import fnmatch
from common.collectionutils.renameutils import find_or_create_directory
from gallery import locations
from gallery.locations import COLLECTION_PHYS_ROOT

from gallery.models import Image

META_ROOT = os.path.join(COLLECTION_PHYS_ROOT, '.meta')
PID_FILE = os.path.join(META_ROOT, "indexer.pid")
LOG_FILE = os.path.join(META_ROOT, "indexer.log")

class Indexer():
    JPG_MATCH = re.compile(fnmatch.translate('*.JPG'), re.IGNORECASE)

    @classmethod
    def walk(cls):
        for (root, dirs, files) in os.walk(COLLECTION_PHYS_ROOT):
            # ignore directories starting with a dot
            dirs[:] = [x for x in dirs if not x.startswith('.')]
            dirs.sort(key=lambda x: x.lower())
            images = [f for f in sorted(files) if cls.JPG_MATCH.match(f)]

            # find directory corresponding to root -> create if needed
            root_web_path = locations.collection_web_path(root)
            root_object = find_or_create_directory(root_web_path)
            root_modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(root))

            # update underlying objects only if:
            # a) root is new directory (modification_time is None)
            # b) modification time has changed
            if (root_object.modification_time is None or
                        root_object.modification_time < root_modification_time):
                root_object.modification_time != root_modification_time

                # if any of directories under root doesn't exist -> remove it from db
                for directory_object in root_object.subdirectories.all():
                    if os.path.basename(directory_object.path) not in dirs:
                        logging.info("Removing directory: " + directory_object.path)
                        directory_object.delete()

                # if any of images under root doesn't exist -> remove it from db
                for image_object in root_object.images.all():
                    if image_object.name not in images:
                        logging.info("Removing image: " + image_object.path)
                        image_object.delete()

                # add directory objects if not found on db
                directories_on_db = {os.path.basename(x.path) for x in (root_object.subdirectories.all())}
                for directory in set(dirs) - directories_on_db:
                    dir_web_path = os.path.join(root_web_path, directory)
                    find_or_create_directory(dir_web_path, parent=root_object)
                    logging.info("Adding directory: " + dir_web_path)

                # add directory objects if not found on db
                images_on_db = {x.name for x in (root_object.images.all())}
                for image in set(images) - images_on_db:
                    image_object = Image(name=image, directory=root_object)
                    image_object.save()
                    logging.info("Adding file " + image_object.path)


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s (%(levelname)s): %(message)s", filename=LOG_FILE, level=logging.INFO)
    handle_pidfile(PID_FILE)
    Indexer.walk()