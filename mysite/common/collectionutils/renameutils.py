import os

def move_without_overwriting(src, dst):
    if os.path.exists(dst):
        raise "File {} exists".format(dst)
    os.rename(src, dst)