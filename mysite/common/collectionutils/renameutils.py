import datetime
import logging
import os


from common.collectionutils.misc import localized_time
from gallery import locations
from gallery.models import Directory

logger = logging.getLogger(__name__)

def get_mtime_datetime(path):
    return localized_time(datetime.datetime.fromtimestamp(os.path.getmtime(path)))


def move_without_overwriting(src, dst, create_destination_dir=False):
    # Source and destination files should exist
    if os.path.exists(dst):
        raise Exception("File {} exists".format(dst))

    if not os.path.exists(src):
        raise Exception("File {} doesn't exist".format(src))

    # Destination folder doesn't exist
    dst_dir = os.path.dirname(dst)
    if not os.path.exists(dst_dir):
        if create_destination_dir:
            os.makedirs(dst_dir)
        else:
            raise Exception("Destination folder {} doesn't exist".format(dst_dir))

    os.rename(src, dst)


def find_or_create_directory(web_path, parent=None, update_modification_time=False):
    directory_mtime = get_mtime_datetime(locations.collection_phys_path(web_path))
    directory, created = Directory.objects.get_or_create(path=web_path,
                                                defaults={'modification_time': directory_mtime, 'parent': parent})
    if update_modification_time and directory.modification_time != directory_mtime:
        logger.info("updating directory mtime: " + directory.path)
        directory.modification_time = directory_mtime
        directory.save()

    return directory
