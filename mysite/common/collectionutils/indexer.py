from datetime import datetime
import logging
import os
import re

from django.db.models import Q, Count

from common.collectionutils.misc import localized_time, is_jpeg, is_video
from common.collectionutils.renamer import Renamer
from common.collectionutils.renameutils import find_or_create_directory, get_mtime_datetime
from gallery import locations
from gallery.models import Image, ImageGroup, Video


logger = logging.getLogger(__name__)


class Indexer():
    """
    Keeps database objects in sync with collection of images.
    Traverses image collection and removes outdated objects or creates missing ones.
    """

    @classmethod
    def post_indexing_fixes(cls):
        cls._fix_image_properties()
        cls._delete_empty_image_groups()

    @classmethod
    def synchronize_db_with_collection(cls, root, dirs, files):
        cls._process_directory(root, dirs, files)

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
    def _process_files(cls, files, root_object, root_phys_path):
        # if any of images under root doesn't exist -> remove it from db
        for file_object in root_object.files.all():
            if file_object.name not in files:
                logger.info("removing file: " + file_object.path)
                file_object.delete()

        # add file objects if not found on db
        files_on_db = {x.name for x in (root_object.files.all())}
        for missing_file in set(files) - files_on_db:
            file_mtime = get_mtime_datetime(os.path.join(root_phys_path, missing_file))

            if is_jpeg(missing_file):
                file_class = Image
            elif is_video(missing_file):
                file_class = Video

            file_object = file_class(name=missing_file, directory=root_object, modification_time=file_mtime)
            file_object.save()
            logger.info("adding file " + file_object.path)

    @classmethod
    def assign_image_to_image_group(cls, image):
        # create or find image group based on date in image name => assign it to image
        date_time_match = re.match(r'\d{8}_\d{6}', image.name)
        if date_time_match:
            date_time = date_time_match.group(0)
            image_group, created = ImageGroup.objects.get_or_create(time_string=date_time)
            image.image_group = image_group
            image.save()
            logging.info("added image {} to group {}".format(image.name, image_group.time_string))

    @classmethod
    def _fix_image_properties(cls):
        # assign any non assigned images to image group
        for image in Image.objects.filter(image_group__isnull=True):
            cls.assign_image_to_image_group(image)

        # for all images in Trash with empty trash_time, set it to current timestamp
        count = Image.objects \
            .filter(Q(directory__path__startswith='Trash/') | Q(directory__path__exact='Trash')) \
            .filter(trash_time__isnull=True) \
            .update(trash_time=(localized_time(datetime.now())))

        if count:
            logging.info("updated trash_time of {} trashed images.".format(count))

    @classmethod
    def _delete_empty_image_groups(cls):
        # remove image groups having no images
        empty_image_groups = ImageGroup.objects.annotate(num_images=Count('images')).filter(num_images__lte=0)
        count = empty_image_groups.count()

        if count:
            empty_image_groups.delete()
            logging.info("removed {} unneeded image groups".format(count))

    @classmethod
    def _process_directory(cls, root_phys_path, dirs, files):
        # only index files that have correct name - it will be changed anyway during next Runner loop
        files = sorted([f for f in files if is_jpeg(f) and Renamer.CORRECT_FILENAME_RE.match(f) or is_video(f)])

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

            cls._process_files(files, root_object, root_phys_path)
