from datetime import timedelta, datetime
import logging
import os

from django.db.models import Q
from pytz import timezone

from gallery import locations
from gallery.models import Image
from mysite import settings


class TrashCleaner(object):
    """ Remove images moved to trash month ago or earlier. """

    @staticmethod
    def go():
        month_before = datetime.now(timezone(settings.TIME_ZONE)) - timedelta(days=30)

        # select images from trash that were moved month before or earlier
        old_images_in_trash = Image.objects \
            .filter(Q(directory__path__startswith='Trash/') | Q(directory__path__exact='Trash')) \
            .filter(trash_time__lte=month_before)

        # remove file in collection
        # thumbnails and database object will be removed by Thumbnailer and Indexer respectively
        for image in old_images_in_trash:
            image_phys_path = locations.collection_phys_path(image.path)
            logging.info("Removing outdated file in trash: " + image_phys_path)
            os.unlink(image_phys_path)
