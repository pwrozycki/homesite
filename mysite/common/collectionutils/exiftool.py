import json
import os
import subprocess
import datetime
import logging

EXIF_DATE_FIELDS = [
    'DateTimeOriginal',
    'DateTime',
    'FileModifyDate'
]
EXIF_FILE_NUMBER = 'FileNumber'
EXIFTOOL_FIELD_ARGS = ['-dateFormat', "%Y:%m:%d %H:%M:%S"] + \
                      ["-" + x for x in EXIF_DATE_FIELDS + [EXIF_FILE_NUMBER]]

EXIF_DATE_FORMAT = "%Y:%m:%d %H:%M:%S"
FILE_DATE_FORMAT = "%Y%m%d_%H%M%S"


class JsonUtil:
    @staticmethod
    def read_exiftool_json(files):
        output_bytes = subprocess.check_output(["exiftool", "-json"] + EXIFTOOL_FIELD_ARGS + files,
                                               stderr=open(os.devnull, 'w'))
        output_str = output_bytes.decode(encoding='UTF-8')
        return json.loads(output_str)


class ImageInfo:
    def __init__(self, path, date, file_number):
        self.path = path
        self.extension = os.path.splitext(self.filename)[1].lower()
        self.date = date
        self.file_number = file_number
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
    def create_from_json(cls, exif_json):
        path = os.path.abspath(exif_json.get('SourceFile'))
        file_number = exif_json.get(EXIF_FILE_NUMBER, None)
        date = cls.read_date_info(exif_json)
        return ImageInfo(path, date, file_number)

    @staticmethod
    def read_date_info(exif_json):
        for exifField in EXIF_DATE_FIELDS:
            date_info = exif_json.get(exifField, '')
            if date_info != '':
                try:
                    date = datetime.datetime.strptime(date_info, EXIF_DATE_FORMAT)
                    return date
                except ValueError:
                    logging.error('unable to parse date: {0}: {1}: '.format(exif_json['SourceFile'], date_info))
                    continue

        return None

    def __repr__(self):
        return "date:{0.date}, file_number:{0.file_number}, fileName:{0.filename}, suffix:{0.suffix}, newFile:{0.new_filename}".format(
            self)