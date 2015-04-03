import logging
import os
import subprocess

from django.db.models.query_utils import Q

from common.collectionutils.thumbnailer import Thumbnailer
from gallery import locations
from gallery.models import Image


try:
    from gi.repository.GExiv2 import Metadata
except ImportError:
    from gi.repository.GExiv2 import Metadata

logger = logging.getLogger(__name__)


class Rotator:
    """
    Performs rotation based on Image.orientation field.
    After rotation orientation is reset to neutral value - up.
    """

    # jpegtran version constants
    ROTATIONS_MAP = {'right': 270, 'down': 180, 'left': 90}

    @classmethod
    def _rotate_by_jpegtran(cls, image_phys_path, rotated_image):
        image_phys_path_rotated = image_phys_path + "_rotated"
        rotation_angle = str(cls.ROTATIONS_MAP[rotated_image.orientation])

        logger.info("rotating image ({} degrees): {}".format(rotation_angle, image_phys_path))

        # call lossless rotation
        subprocess.call(
            ['jpegtran', '-rotate', rotation_angle, '-outfile', image_phys_path_rotated, image_phys_path])

        # overwrite original, preserve timestamp
        old_mtime = os.path.getmtime(image_phys_path)
        os.rename(image_phys_path_rotated, image_phys_path)
        os.utime(image_phys_path, (-1, old_mtime))

        # invoke thumbnail recreation
        Thumbnailer.create_thumbnails(image_phys_path, force_recreate=True)

        # write "normal" image orientation to database
        rotated_image.orientation = 'up'
        rotated_image.save()

    @classmethod
    def go(cls):
        for rotated_image in Image.objects.filter(~Q(orientation='up')):
            image_phys_path = locations.collection_phys_path(rotated_image.path)

            cls._rotate_by_jpegtran(image_phys_path, rotated_image)



