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
        date = cls.read_date_info(path)
        return ImageInfo(path, date)

    @staticmethod
    def get_exif_metadata(path):
        try:
            metadata = Metadata()
            metadata.open_path(path)
            return metadata
        except Exception:
            logging.error('error reading metadata: {0}'.format(path))

        return None

    @classmethod
    def read_date_info(cls, path):
        # try to read metadata
        metadata = cls.get_exif_metadata(path)

        # Try to read date information from exif tags
        # (if metadata was read correctly)
        if metadata:
            for exif_field in EXIF_DATE_FIELDS:
                date_info = metadata.get_tag_string(exif_field)
                if date_info:
                    try:
                        date = datetime.datetime.strptime(date_info, EXIF_DATE_FORMAT)
                        return date
                    except ValueError:
                        # Date didn't match expected format - log error
                        logging.error('unable to parse date: {0}: {1}: '.format(path, date_info))
                else:
                    # There was no matching date for given exif field -> try next one
                    logging.info('missing field: {} in {}'.format(exif_field, path))

        # If file has no valid date information - return modification time
        return datetime.datetime.fromtimestamp(os.path.getmtime(path))

    def __repr__(self):
        return "date:{0.date}, fileName:{0.filename}, suffix:{0.suffix}, newFile:{0.new_filename}".format(
            self)