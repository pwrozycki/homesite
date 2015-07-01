import logging
import os
import subprocess

from django.db.models.query_utils import Q
from common.collectionutils.indexer import Indexer
from common.collectionutils.renameutils import get_mtime_datetime

from common.collectionutils.thumbnailer import Thumbnailer
from gallery import locations
from gallery.models import Image


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

        os.rename(image_phys_path_rotated, image_phys_path)

        # invoke thumbnail recreation
        Thumbnailer.create_miniatures(image_phys_path, force_recreate=True)

        # reset image orientation
        rotated_image.orientation = 'up'
        # recalculate aspect radio, modification_time
        rotated_image.aspect_ratio = Indexer.get_image_aspect_ratio(image_phys_path)
        rotated_image.modification_time = get_mtime_datetime(image_phys_path)

        rotated_image.save()

    @classmethod
    def perform_requested_rotations(cls):
        for rotated_image in Image.objects.filter(~Q(orientation='up')):
            image_phys_path = locations.collection_phys_path(rotated_image.path)

            cls._rotate_by_jpegtran(image_phys_path, rotated_image)



