import re

import pytz
from django.utils import timezone

JPG_EXTENSION_RE = re.compile(r'^.*\.(?:jpg)$', re.IGNORECASE)
VIDEO_EXTENSION_RE = re.compile(r'^.*\.(?:mp4|m4v|3gp|m4a|mov|avi|vob|wmv|mts)$', re.IGNORECASE)


def utc_to_defaulttz(time):
    return pytz.utc.localize(time).astimezone(timezone.get_default_timezone())


def is_video(f):
    return VIDEO_EXTENSION_RE.match(f)


def is_jpeg(f):
    return JPG_EXTENSION_RE.match(f)
