from datetime import timedelta

from django.utils import timezone
from pytz.exceptions import AmbiguousTimeError


def localized_time(time):
    try:
        return timezone.make_aware(time, timezone.get_default_timezone())
    except AmbiguousTimeError:
        return localized_time(time + timedelta(hours=1))
