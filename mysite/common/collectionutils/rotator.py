import logging
import os
import subprocess

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from common import debugtool
from common.collectionutils.thumbnailer import Thumbnailer
from django.db.models.query_utils import Q
from gallery import locations
from gallery.models import Image

try:
    from gi.repository.GExiv2 import Metadata
except ImportError:
    from gi.repository.GExiv2 import Metadata

logger = logging.getLogger(__name__)


class Rotator:
    # EXIF version constants
    # how many times image should be rotated left to achieve upright orientation
    ORIENTATIONS_MAP = {'up': 0, 'right': 1, 'down': 2, 'left': 3}
    # consecutive left rotations
    ORIENTATIONS = [1, 8, 3, 6]
    # meaning of exif values
    EXIF_MISSING_ORIENTATION = 0
    EXIF_ORIENTATION_UP = 1

    # jpegtran version constants
    ROTATIONS_MAP = {'right': 270, 'down': 180, 'left': 90}

    @classmethod
    def _calculate_new_orientation(cls, image_orientation, metadata_orientation):
        rotate_left_count = cls.ORIENTATIONS_MAP[image_orientation]
        orientation_index = cls.ORIENTATIONS.index(metadata_orientation)
        new_orientation_index = (orientation_index + rotate_left_count) % len(cls.ORIENTATIONS)
        new_orientation = cls.ORIENTATIONS[new_orientation_index]

        return new_orientation

    @classmethod
    def rotate_by_exif_tag(cls, image_phys_path, rotated_image):
        metadata = Metadata()
        metadata.open_path(image_phys_path)
        metadata_orientation = metadata.get_orientation().real

        # no orientation means exactly the same as UP
        if metadata_orientation == cls.EXIF_MISSING_ORIENTATION:
            metadata_orientation = cls.EXIF_ORIENTATION_UP
        image_orientation = rotated_image.orientation
        new_orientation = cls._calculate_new_orientation(image_orientation, metadata_orientation)
        metadata.set_orientation(new_orientation)

        # save metadata but preserve mtime
        old_mtime = os.path.getmtime(image_phys_path)
        metadata.save_file(image_phys_path)
        os.utime(image_phys_path, (-1, old_mtime))

        # invoke thumbnail recreation
        Thumbnailer.create_thumbnails(image_phys_path, force_recreate=True)
        rotated_image.orientation = "up"
        rotated_image.save()

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



