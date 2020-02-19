import logging
import os
import re
import subprocess
import sys
from abc import ABCMeta, abstractmethod
from contextlib import suppress

import tzlocal
from pymediainfo import MediaInfo

from common.collectionutils.misc import is_video, is_jpeg
from common.collectionutils.renamer import Renamer
from common.collectionutils.renameutils import get_mtime_datetime
from gallery import locations
from gallery.locations import COLLECTION_PHYS_ROOT, VIDEOS_PHYS_ROOT, THUMBNAILS_PHYS_ROOT, PREVIEW_PHYS_ROOT
from gallery.models import File

logger = logging.getLogger(__name__)


class GeneratorBase(metaclass=ABCMeta):
    def extension(self):
        return ''

    def _name_miniature_to_original(self, f):
        pattern = TIMESTAMP_PATTERN + re.escape(self.extension()) + r'$'
        return re.sub(pattern, '', f, flags=re.IGNORECASE)

    def _name_original_to_miniature(self, f):
        if os.path.exists(f):
            timestamp = get_mtime_datetime(f)
        else:
            try:
                directory, filename = os.path.split(locations.collection_web_path(f))
                timestamp = File.objects.all().get(name=filename, directory__path=directory).modification_time
                timestamp = timestamp.astimezone(tzlocal.get_localzone())
            except File.DoesNotExist:
                raise Exception("File should either exist or be present on database " + f)
        return f + "_" + timestamp.strftime(TIMESTAMP_FORMAT) + self.extension()

    @abstractmethod
    def miniatures_root(self):
        pass

    @staticmethod
    def _change_path_root(prev_root, new_root, path):
        path = os.path.normpath(path)
        prev_root = os.path.normpath(prev_root)
        new_root = os.path.normpath(new_root)
        if not path.startswith(prev_root):
            logger.critical("terminating: path should be rooted in: {}".format(prev_root))
            sys.exit(-1)
        return re.sub('^' + prev_root, new_root, path)

    def miniature_phys_path(self, collection_phys_path, is_directory=False):
        tmp_path = collection_phys_path if is_directory else self._name_original_to_miniature(collection_phys_path)
        return self._change_path_root(COLLECTION_PHYS_ROOT, self.miniatures_root(), tmp_path)

    def collection_phys_path(self, miniature_phys_path, is_directory=False):
        tmp_path = miniature_phys_path if is_directory else self._name_miniature_to_original(miniature_phys_path)
        return self._change_path_root(self.miniatures_root(), COLLECTION_PHYS_ROOT, tmp_path)


class VideoGenerator(GeneratorBase):
    def will_output_file(self, f):
        return is_video(f)

    def extension(self):
        return '.mp4'

    def miniatures_root(self):
        return VIDEOS_PHYS_ROOT

    def _get_rotation(self, input_file):
        video_track_infos = [t for t in MediaInfo.parse(input_file).tracks if t.track_type == 'Video']
        if not video_track_infos:
            return 0

        rotation = video_track_infos[0].rotation
        if not rotation:
            return 0

        return int(float(rotation))

    def _rotation_arg(self, input_path):
        rotation = self._get_rotation(input_path)
        rotation_arg = "rotate={}/180*PI".format(rotation)
        if rotation % 180 == 90:
            rotation_arg += ":ow=ih:oh=iw"
        return rotation_arg

    def generate_miniature(self, input_path, output_path):
        logger.info("creating video: {}".format(output_path))

        transformation = ["-strict", "-2", "-vf", self._rotation_arg(input_path), '-c:v', 'libx264', '-crf', '22',
                          '-pix_fmt', 'yuv420p', '-y', '-threads', '4', '-metadata:s:v:0', 'rotate=0']

        self._call_ffmpeg(transformation, input_path, output_path)

    def _call_ffmpeg(self, ffmpeg_transformation, input_path, output_path):
        (output_path_without_extension, extension) = os.path.splitext(output_path)
        tmp_output_path = output_path_without_extension + "_tmp" + extension

        with open(os.devnull, 'w') as null:
            ffmpeg_args = ['ffmpeg', '-i', input_path] + ffmpeg_transformation + [tmp_output_path]
            return_code = subprocess.call(ffmpeg_args, stdout=null, stderr=null)

        if return_code != 0:
            logging.error("ffmpeg returned non-zero return code: {}".format(return_code))
            with suppress(OSError):
                os.unlink(tmp_output_path)
        else:
            os.rename(tmp_output_path, output_path)


class FirstFrameGenerator(VideoGenerator):
    def extension(self):
        return '.jpg'

    def generate_miniature(self, input_path, output_path):
        with open(os.devnull, 'w') as null:
            logger.info("creating video shot: {}".format(output_path))

            rotation = self._rotation_arg(input_path)
            transformation = ['-vf', rotation + ',scale=iw*min(320/iw\,240/ih):ih*min(320/iw\,240/ih)',
                              '-vframes', '1', '-f', 'image2', '-y']

            self._call_ffmpeg(transformation, input_path, output_path)


class ThumbnailGenerator(GeneratorBase):
    def __init__(self, mode, geometry, miniatures_root):
        self._mode = mode
        self._geometry = geometry
        self._miniatures_root = miniatures_root

    def extension(self):
        return '.jpg'

    def will_output_file(self, f):
        return bool(is_jpeg(f) and Renamer.CORRECT_FILENAME_RE.match(f))

    def miniatures_root(self):
        return self._miniatures_root

    def generate_miniature(self, input_path, output_path):
        logger.info("creating image: {}".format(output_path))
        subprocess.call(['convert', input_path, '-auto-orient',
                         self._mode, self._geometry, '-quality', '80', output_path])


TIMESTAMP_FORMAT = "%y%m%d:%H%M%S"
TIMESTAMP_PATTERN = r'_\d{6}:\d{6}'

MINIATURE_GENERATORS = [
    ThumbnailGenerator('-thumbnail', 'x200', THUMBNAILS_PHYS_ROOT),
    ThumbnailGenerator('-resize', 'x1280', PREVIEW_PHYS_ROOT),
    VideoGenerator(),
    FirstFrameGenerator(),
]
