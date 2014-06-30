import os

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