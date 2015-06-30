from datetime import timedelta
import re

from django.utils import timezone
from pytz.exceptions import AmbiguousTimeError


JPG_EXTENSION_RE = re.compile(r'^.*\.(?:jpg)$', re.IGNORECASE)
VIDEO_EXTENSION_RE = re.compile(r'^.*\.(?:mp4|m4v|3gp|m4a|mov|avi|vob)$', re.IGNORECASE)


def localized_time(time):
    try:
        return timezone.make_aware(time, timezone.get_default_timezone())
    except AmbiguousTimeError:
        return localized_time(time + timedelta(hours=1))


def is_video(f):
    return VIDEO_EXTENSION_RE.match(f)


def is_jpeg(f):
    return JPG_EXTENSION_RE.match(f)
