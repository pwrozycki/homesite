import os
from gallery import locations
from gallery.models import Directory


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

def find_or_create_directory(web_path, parent=None):
    queryset = Directory.objects.filter(path=web_path)
    if queryset:
        return queryset[0]

    directory_instance = Directory(path=web_path, parent=parent,
                                   thumbnail_path=locations.thumbnail_web_path(web_path),
                                   preview_path=locations.preview_web_path(web_path))
    directory_instance.save()
    return directory_instance