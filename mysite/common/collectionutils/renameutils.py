import datetime
import os

from common.collectionutils.misc import localized_time
from gallery import locations
from gallery.models import Directory


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


def find_or_create_directory(web_path, parent=None, save_modification_time=True):
    # TODO: replace with get_or_create
    # TODO: remove save_modification_time (and the notion that directory with modification_time unset is unprocessed)
    queryset = Directory.objects.filter(path=web_path)

    # if directory exists return from queryset
    if queryset:
        return queryset[0]

    # if directory doesn't exists - create it
    else:
        directory_instance = Directory(path=web_path, parent=parent)

        if save_modification_time:
            path = locations.collection_phys_path(web_path)
            directory_instance.modification_time = get_mtime_datetime(path)

        directory_instance.save()
        return directory_instance