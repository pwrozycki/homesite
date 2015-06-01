import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler
import os
import traceback
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from common.collectionutils.rotator import Rotator

from common.collectionutils.trash_cleaner import TrashCleaner
from gallery.locations import COLLECTION_PHYS_ROOT, collection_walk
from common.collectionutils.indexer import Indexer
from common.collectionutils.renamer import Renamer
from common.collectionutils.thumbnailer import Thumbnailer
from common.collectionutils.pidfile import handle_pidfile


class Runner:
    """
    Runs task to manage various aspects of gallery.
    """
    LOG_FILE = os.path.join(COLLECTION_PHYS_ROOT, '.meta', 'runner.log')

    @classmethod
    def _configure_logging(cls):
        # configure logging
        logger = logging.getLogger()

        logger.setLevel(logging.INFO)

        file_handler = RotatingFileHandler(cls.LOG_FILE, maxBytes=1024 * 1024, backupCount=8)
        file_handler.setFormatter(Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

        logger.addHandler(file_handler)

    @classmethod
    def go(cls):
        django.setup()
        # configure logging
        cls._configure_logging()

        # create pidfile, exit if creation fails
        handle_pidfile(os.path.join(COLLECTION_PHYS_ROOT, '.meta', 'gallery_runner.pid'))

        Rotator.perform_requested_rotations()
        TrashCleaner.remove_old_trash_files()

        for (root, dirs, files) in collection_walk():
            renamed = Renamer.rename_jpgs_in_collection(root, dirs, files)
            Thumbnailer.synchronize_miniatures_with_collection(root, dirs, renamed)
            Indexer.synchronize_db_with_collection(root, dirs, renamed)

        Indexer.post_indexing_fixes()

        Thumbnailer.remove_obsolete()


if __name__ == '__main__':
    try:
        Runner.go()
    except Exception:
        # log any uncaught exceptions
        logging.error("Following unhandled exception occurred:\n{}".format(traceback.format_exc()))