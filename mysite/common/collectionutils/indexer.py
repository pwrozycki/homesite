from datetime import datetime
import logging
import os
import re
import fnmatch

from django.db.models import Q

from django.utils import timezone

from gallery.locations import collection_walk

from common.collectionutils.renameutils import find_or_create_directory, get_mtime_datetime
from gallery import locations
from gallery.models import Image, ImageGroup


logger = logging.getLogger(__name__)


class Indexer():
    JPG_MATCH = re.compile(fnmatch.translate('*.JPG'), re.IGNORECASE)

    @classmethod
    def walk(cls):
        for (root, dirs, files) in collection_walk():
            cls._process_directory(root, dirs, files)

        cls._fix_image_properties()

    @classmethod
    def _process_directories(cls, dirs, root_object, root_web_path):
        # if any of directories under root doesn't exist -> remove it from db
        for directory_object in root_object.subdirectories.all():
            if os.path.basename(directory_object.path) not in dirs:
                logger.info("removing directory: " + directory_object.path)
                directory_object.delete()

        # add directory objects if not found on db
        directories_on_db = {os.path.basename(x.path) for x in (root_object.subdirectories.all())}
        for directory in set(dirs) - directories_on_db:
            dir_web_path = os.path.join(root_web_path, directory)

            # don't save modification time - defer until processing that directory
            find_or_create_directory(dir_web_path, parent=root_object, save_modification_time=False)
            logger.info("adding directory: " + dir_web_path)

    @classmethod
    def _process_images(cls, images, root_object, root_phys_path):
        # if any of images under root doesn't exist -> remove it from db
        for image_object in root_object.images.all():
            if image_object.name not in images:
                logger.info("removing image: " + image_object.path)
                image_object.delete()

        # add image objects if not found on db
        images_on_db = {x.name for x in (root_object.images.all())}
        for image in set(images) - images_on_db:
            image_mtime = get_mtime_datetime(os.path.join(root_phys_path, image))
            image_object = Image(name=image, directory=root_object, modification_time=image_mtime)
            image_object.save()
            logger.info("adding file " + image_object.path)

    @classmethod
    def assign_image_to_image_group(cls, image):
        date_time_match = re.match(r'\d{8}_\d{6}', image.name)
        if date_time_match:
            date_time = date_time_match.group(0)
            image_group, created = ImageGroup.objects.get_or_create(time_string=date_time)
            image.image_group = image_group
            image.save()
            logging.info("Added image {} to group {}".format(image.name, image_group.time_string))

    @classmethod
    def _fix_image_properties(cls):
        # assign any non assigned images to image group
        for image in Image.objects.filter(image_group__isnull=True):
            cls.assign_image_to_image_group(image)

        # for all images in Trash with empty trash_time, set it to current timestamp
        now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
        Image.objects \
            .filter(Q(directory__path__startswith='Trash/') | Q(directory__path__exact='Trash')) \
            .filter(trash_time__isnull=True) \
            .update(trash_time=now)

    @classmethod
    def _process_directory(cls, root_phys_path, dirs, files):
        # ignore directories starting with a dot
        images = sorted([f for f in files if cls.JPG_MATCH.match(f)])

        # find directory object corresponding to root -> create if needed
        root_web_path = locations.collection_web_path(root_phys_path)
        root_object = find_or_create_directory(root_web_path, save_modification_time=False)
        root_modification_time = get_mtime_datetime(root_phys_path)

        # update underlying objects only if:
        # a) root is new directory (modification_time is None)
        # b) modification time has changed
        if (root_object.modification_time is None or
                    root_object.modification_time < root_modification_time):
            root_object.modification_time = root_modification_time
            root_object.save()

            cls._process_directories(dirs, root_object, root_web_path)

            cls._process_images(images, root_object, root_phys_path)
