import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import re
import fnmatch
from common.collectionutils.renameutils import find_or_create_directory
from gallery import locations
from gallery.locations import COLLECTION_PHYS_ROOT

from gallery.models import Directory, Image


class Indexer():
    JPG_MATCH = re.compile(fnmatch.translate('*.JPG'), re.IGNORECASE)

    @classmethod
    def walk(cls):
        for (root, dirs, files) in os.walk(COLLECTION_PHYS_ROOT):
            dirs[:] = [x for x in dirs if not x.startswith('.')]
            dirs.sort(key=lambda x: x.lower())

            # find directory corresponding to root
            # persist directory object
            root_web_path = locations.collection_web_path(root)
            root_directory_object = find_or_create_directory(root_web_path)

            # add directory objects
            for directory in dirs:
                dir_web_path = os.path.join(root_web_path, directory)
                find_or_create_directory(dir_web_path, parent=root_directory_object)

            # find image corresponding to jpg
            # persist if doesn't exist
            for name in [f for f in sorted(files) if cls.JPG_MATCH.match(f)]:
                image_web_path = os.path.abspath(os.path.join(root_web_path, name))
                image_object = Image.objects.filter(name=name, directory__path=root_web_path)
                if not image_object:
                    image_object = Image(name=name, directory=root_directory_object)
                    image_object.save()

    @staticmethod
    def remove_obsolete():
        for image in Image.objects.all():
            image_web_path = os.path.join(image.directory.path, image.name)
            image_phys_path = locations.collection_phys_path(image_web_path)
            if not os.path.exists(image_phys_path):
                image.delete()

        for directory in Directory.objects.all():
            directory_phys_path = locations.collection_phys_path(directory.path)
            if not os.path.exists(directory_phys_path):
                directory.delete()


if __name__ == '__main__':
    Indexer.walk()
    Indexer.remove_obsolete()
