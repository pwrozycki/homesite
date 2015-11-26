from datetime import datetime
import logging
import os
import re

from django.db.models import Q, Count

from gi.repository.GExiv2 import Metadata
from common.collectionutils.misc import localized_time, is_jpeg, is_video
from common.collectionutils.renamer import Renamer
from common.collectionutils.renameutils import find_or_create_directory, get_mtime_datetime
from gallery import locations
from gallery.locations import collection_phys_path
from gallery.models import Image, ImageGroup, Video

logger = logging.getLogger(__name__)


class Indexer:
    """
    Keeps database objects in sync with collection of images.
    Traverses image collection and removes outdated objects or creates missing ones.
    """

    def __init__(self):
        self._removals = []

    @classmethod
    def post_indexing_fixes(cls):
        cls._fix_image_properties()
        cls._delete_empty_image_groups()

    def _process_directories(self, fs_dirnames, root_object, root_web_path):
        # if any of directories under root doesn't exist -> remove it from db
        db_dirs = root_object.subdirectories.all()
        for directory_object in db_dirs:
            if os.path.basename(directory_object.path) not in fs_dirnames:
                logger.info("scheduling directory removal: " + directory_object.path)
                self._removals.append(directory_object)

        # add directory objects if not found on db
        db_dirnames = {os.path.basename(x.path) for x in db_dirs}
        for directory in set(fs_dirnames) - db_dirnames:
            dir_web_path = os.path.join(root_web_path, directory)

            # don't save modification time - defer until processing that directory
            find_or_create_directory(dir_web_path, parent=root_object)
            logger.info("adding directory: " + dir_web_path)

    def _process_files(self, fs_filenames, root_object, root_phys_path):
        db_files = root_object.files.all()
        for file_object in db_files:
            if file_object.name not in fs_filenames:
                # if any of images under root doesn't exist -> remove it from db
                logger.info("scheduling file removal: " + file_object.path)
                self._removals.append(file_object)
            else:
                # update mtime if neeeded
                self._update_mtime_if_needed(file_object)

        # add file objects if not found on db
        db_filenames = {x.name for x in db_files}
        for missing_file in set(fs_filenames) - db_filenames:
            file_phys_path = os.path.join(root_phys_path, missing_file)
            file_mtime = get_mtime_datetime(file_phys_path)

            if is_jpeg(missing_file):
                aspect_ratio = self.get_image_aspect_ratio(file_phys_path)
                file_object = Image(name=missing_file, directory=root_object, modification_time=file_mtime,
                                    aspect_ratio=aspect_ratio)
            elif is_video(missing_file):
                file_object = Video(name=missing_file, directory=root_object, modification_time=file_mtime)
            else:
                raise Exception("File should be either Image or Video" + missing_file)

            file_object.save()
            logger.info("adding file " + file_object.path)

    @classmethod
    def _update_mtime_if_needed(cls, file_object):
        file_phys_path = collection_phys_path(file_object.path)
        mtime = get_mtime_datetime(file_phys_path)
        if file_object.modification_time != mtime:
            logger.info("updating file mtime (and possibly: aspect_ratio): " + file_object.path)
            file_object.modification_time = mtime
            file_object.aspect_ratio = cls.get_image_aspect_ratio(file_phys_path)
            file_object.save()

    @classmethod
    def get_image_aspect_ratio(cls, file_phys_path):
        metadata = Metadata()
        metadata.open_path(file_phys_path)
        aspect_ratio = metadata.get_pixel_width() / metadata.get_pixel_height()

        # sideways rotation -> 90 or 270 degrees aspect ratio should be inverted
        if metadata.get_tag_long('Exif.Image.Orientation') in (6, 8):
            aspect_ratio = 1 / aspect_ratio

        return aspect_ratio

    @classmethod
    def _assign_image_to_image_group(cls, image):
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
            cls._assign_image_to_image_group(image)

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

    def synchronize_db_with_collection(self, root_phys_path, dirs, files):
        # only index files that have correct name - it will be changed anyway during next Runner loop
        files = sorted([f for f in files if is_jpeg(f) and Renamer.CORRECT_FILENAME_RE.match(f) or is_video(f)])

        # find directory object corresponding to root -> create if needed
        root_web_path = locations.collection_web_path(root_phys_path)
        root_object = find_or_create_directory(root_web_path)

        self._process_directories(dirs, root_object, root_web_path)

        self._process_files(files, root_object, root_phys_path)

    def process_pending_removals(self):
        for removal in self._removals:
            removal.delete()
