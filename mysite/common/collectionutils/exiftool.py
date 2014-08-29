import os
import datetime
import logging

try:
    from gi.repository.GExiv2 import Metadata
except ImportError:
    from gi.repository.GExiv2 import Metadata

EXIF_DATE_FIELDS = [
    'Exif.Photo.DateTimeOriginal',
    'Exif.Image.DateTime',
]

EXIF_DATE_FORMAT = "%Y:%m:%d %H:%M:%S"
FILE_DATE_FORMAT = "%Y%m%d_%H%M%S"


class ImageInfo:
    def __init__(self, path, date):
        self.path = path
        self.extension = os.path.splitext(self.filename)[1].lower()
        self.date = date
        self.suffix = None

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def new_path(self):
        return os.path.join(os.path.dirname(self.path), self.new_filename)

    @property
    def new_filename(self):
        return (self.date.strftime(FILE_DATE_FORMAT) +
                (("_{}".format(self.suffix)) if self.suffix is not None else "") +
                self.extension)

    @classmethod
    def for_path(cls, path):
        metadata = Metadata()
        metadata.open_path(path)
        date = cls.read_date_info(metadata, path)
        return ImageInfo(path, date)

    @staticmethod
    def read_date_info(metadata, path):
        # Try to read date information from exif tags
        for exifField in EXIF_DATE_FIELDS:
            try:
                date_info = metadata.get_tag_string(exifField)
                if date_info:
                    date = datetime.datetime.strptime(date_info, EXIF_DATE_FORMAT)
                    return date
            except AttributeError:
                # Specific exif tag is missing - try with next one
                pass
            except ValueError:
                # Date didn't match expected format - log error
                logging.error('unable to parse date: {0}: {1}: '.format(path, date_info))
                pass

        # If no tag contains valid date - return modification time
        return datetime.datetime.fromtimestamp(os.path.getmtime(path))

    def __repr__(self):
        return "date:{0.date}, fileName:{0.filename}, suffix:{0.suffix}, newFile:{0.new_filename}".format(
            self)