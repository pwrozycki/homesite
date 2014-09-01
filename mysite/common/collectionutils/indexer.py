import datetime
import logging
import os
from gallery.locations import collection_walk

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import re
import fnmatch
from common.collectionutils.renameutils import find_or_create_directory, get_mtime_datetime
from gallery import locations

from gallery.models import Image

logger = logging.getLogger(__name__)


class Indexer():
    JPG_MATCH = re.compile(fnmatch.translate('*.JPG'), re.IGNORECASE)

    @classmethod
    def walk(cls):
        for (root, dirs, files) in collection_walk():
            cls._process_directory(root, dirs, files)

    @classmethod
    def _process_directory(cls, root, dirs, files):
        # ignore directories starting with a dot
        images = sorted([f for f in files if cls.JPG_MATCH.match(f)])

        # find directory object corresponding to root -> create if needed
        root_web_path = locations.collection_web_path(root)
        root_object = find_or_create_directory(root_web_path, save_modification_time=False)
        root_modification_time = get_mtime_datetime(root)

        # update underlying objects only if:
        # a) root is new directory (modification_time is None)
        # b) modification time has changed
        if (root_object.modification_time is None or
                    root_object.modification_time < root_modification_time):
            root_object.modification_time = root_modification_time
            root_object.save()

            # if any of directories under root doesn't exist -> remove it from db
            for directory_object in root_object.subdirectories.all():
                if os.path.basename(directory_object.path) not in dirs:
                    logger.info("removing directory: " + directory_object.path)
                    directory_object.delete()

            # if any of images under root doesn't exist -> remove it from db
            for image_object in root_object.images.all():
                if image_object.name not in images:
                    logger.info("removing image: " + image_object.path)
                    image_object.delete()

            # add directory objects if not found on db
            directories_on_db = {os.path.basename(x.path) for x in (root_object.subdirectories.all())}
            for directory in set(dirs) - directories_on_db:
                dir_web_path = os.path.join(root_web_path, directory)
                # don't save modification time - defer until processing that directory
                find_or_create_directory(dir_web_path, parent=root_object, save_modification_time=False)
                logger.info("adding directory: " + dir_web_path)

            # add image objects if not found on db
            images_on_db = {x.name for x in (root_object.images.all())}
            for image in set(images) - images_on_db:
                image_mtime = get_mtime_datetime(os.path.join(root, image))
                image_object = Image(name=image, directory=root_object, modification_time=image_mtime)
                image_object.save()
                logger.info("adding file " + image_object.path)