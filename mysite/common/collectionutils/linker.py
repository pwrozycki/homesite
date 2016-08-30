import logging
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from common.collectionutils.generators import VideoGenerator, FirstFrameGenerator
from common.collectionutils.renameutils import get_mtime_datetime
from gallery import locations
from gallery.models import Video

logger = logging.getLogger(__name__)


class Linker(object):
    """
    Mostly used, when user decides that original videos is too big and should be replaced by miniature video.
    Moves miniature video to original collection folder and symlink pointing back in miniature videos folder.
    Original video is removed.
    """
    @classmethod
    def create_links(cls):
        for f in Video.objects.filter(substitute_original=True).order_by('directory__path', 'name'):
            cls._create_links(f)

    @staticmethod
    def _create_links(file):
        video_generator = VideoGenerator()
        original_phys_path = locations.collection_phys_path(file.path)
        new_original_phys_path = os.path.splitext(original_phys_path)[0] + video_generator.extension()

        miniature_phys_path = video_generator.miniature_phys_path(original_phys_path)
        if not os.path.exists(miniature_phys_path):
            logger.warn("Miniature doesn't exist, skipping: {}".format(miniature_phys_path))
            return

        if os.path.islink(miniature_phys_path):
            logger.warn("Miniature is already symbolic link, skipping: {}".format(miniature_phys_path))
            file.substitute_original = False
            file.save()
            return

        logger.info("Swapping original with miniature: {}".format(original_phys_path))

        poster_generator = FirstFrameGenerator()
        # poster phys path has to be calculated before original is overwritten
        poster_phys_path = poster_generator.miniature_phys_path(original_phys_path)

        Linker._move_miniature_to_collection(original_phys_path, new_original_phys_path, video_generator)

        Linker._create_symlink(video_generator, new_original_phys_path)

        Linker._remove_original(original_phys_path, new_original_phys_path)

        Linker._move_poster(poster_phys_path, poster_generator, new_original_phys_path)

        Linker._update_file_information(file, new_original_phys_path)

    @staticmethod
    def _update_file_information(file, new_original_phys_path):
        file.name = os.path.basename(new_original_phys_path)
        file.modification_time = get_mtime_datetime(new_original_phys_path)
        file.substitute_original = False
        file.save()

    @staticmethod
    def _move_poster(poster_phys_path, poster_generator, new_original_phys_path):
        new_poster_phys_path = poster_generator.miniature_phys_path(new_original_phys_path)
        os.rename(poster_phys_path, new_poster_phys_path)

    @staticmethod
    def _remove_original(original_phys_path, new_original_phys_path):
        if original_phys_path != new_original_phys_path:
            os.remove(original_phys_path)

    @staticmethod
    def _move_miniature_to_collection(original_phys_path, new_original_phys_path, video_generator):
        miniature_phys_path = video_generator.miniature_phys_path(original_phys_path)
        os.rename(miniature_phys_path, new_original_phys_path)

    @staticmethod
    def _create_symlink(video_generator, new_original_phys_path):
        """ Create symlink pointing back from miniature to original video """
        new_miniature_phys_path = video_generator.miniature_phys_path(new_original_phys_path)
        os.symlink(new_original_phys_path, new_miniature_phys_path)