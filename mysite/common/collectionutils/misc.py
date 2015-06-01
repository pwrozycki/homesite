from datetime import timedelta
import re
import fnmatch

from django.utils import timezone
from pytz.exceptions import AmbiguousTimeError


JPG_EXTENSION_RE = re.compile(fnmatch.translate('*.JPG'), re.IGNORECASE)
VIDEO_EXTENSION_RE = re.compile(fnmatch.translate('*.mp4'), re.IGNORECASE)


def localized_time(time):
    try:
        return timezone.make_aware(time, timezone.get_default_timezone())
    except AmbiguousTimeError:
        return localized_time(time + timedelta(hours=1))


def is_video(f):
    return VIDEO_EXTENSION_RE.match(f)


def is_jpeg(f):
    return JPG_EXTENSION_RE.match(f)