from datetime import timedelta, datetime
import logging
import os
import glob

from django.db.models import Q

from common.collectionutils.misc import localized_time
from gallery import locations
from gallery.models import Image


class TrashCleaner(object):
    """
    Remove images moved to trash month ago or earlier.
    Also remove all files differing only by extension.
    """
    @staticmethod
    def remove_old_trash_files():
        month_ago = localized_time(datetime.now() - timedelta(days=30))

        # select images from trash that were moved month before or earlier
        old_images_in_trash = Image.objects \
            .filter(Q(directory__path__startswith='Trash/') | Q(directory__path__exact='Trash')) \
            .filter(trash_time__lte=month_ago)

        # remove file in collection
        # thumbnails and database object will be removed by Thumbnailer and Indexer respectively
        for image in old_images_in_trash:
            image_phys_path = locations.collection_phys_path(image.path)
            all_files_with_prefix = set(glob.glob(os.path.splitext(image_phys_path)[0] + ".*"))
            logging.info("Removing outdated files in trash: " + ' '.join(all_files_with_prefix))
            for file_name in all_files_with_prefix:
                os.unlink(file_name)

        # remove directory in trash if empty
        trash_dir_phys_path = locations.collection_phys_path(locations.TRASH_DIR_NAME)
        for (root, dirs, files) in os.walk(trash_dir_phys_path, topdown=False):
            for directory in dirs:
                try:
                    dir_path = os.path.join(root, directory)
                    os.rmdir(dir_path)
                    logging.info("Removing empty directory in trash: " + dir_path)
                except IOError as e:
                    # directory isn't empty - skipping
                    pass


