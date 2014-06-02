import os

def move_without_overwriting(src, dst):
    if os.path.exists(dst):
        raise Exception("File {} exists".format(dst))

    os.rename(src, dst)