import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler
import os

from gallery.locations import COLLECTION_PHYS_ROOT
from common.collectionutils.indexer import Indexer
from common.collectionutils.renamer import Renamer
from common.collectionutils.thumbnailer import Thumbnailer
from common.collectionutils.pidfile import handle_pidfile


class Runner:
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
        # create pidfile, exit if creation fails
        cls._configure_logging()

        handle_pidfile(os.path.join(COLLECTION_PHYS_ROOT, '.meta', 'gallery_runner.pid'))

        for processor in (Renamer, Thumbnailer, Indexer):
            for (root, dirs, files) in os.walk(COLLECTION_PHYS_ROOT):
                dirs[:] = [x for x in dirs if not x.startswith('.')]
                dirs.sort()
                files.sort()

                processor.prepare_phase_hook(root, dirs, files)

        Thumbnailer.remove_obsolete()


if __name__ == '__main__':
    Runner.go()