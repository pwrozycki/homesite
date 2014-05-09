#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import os
import fnmatch
from exiftool import JsonUtil, ImageInfo
from renameutils import move_without_overwriting

EXTENSIONS = ["*.cr2", "*.nef", "*.jpg"]
IMG_RE = re.compile("|".join([fnmatch.translate(mask) for mask in EXTENSIONS]), re.IGNORECASE)

MIN_YEAR = 2000
MAX_YEAR = 2099

class NamingStrategy:
    @classmethod
    def calculate_suffix(cls, prev_info, new_info):
        # jest kolizja nazw
        if cls.conflicts_with(prev_info, new_info):
            (digit, letter) = cls.split_digit_and_letter(prev_info.suffix)

            # jesli numery plikow sa nadane i rowne to jest to kopia (kopia powinna miec przyrostek _a,b,c,d)
            if (prev_info.fileNumberField is not None and
                        prev_info.fileNumberField == new_info.fileNumberField):
                return digit + cls.next_letter(letter)

            # w przeciwnym przypadku po prostu kolejny numerek (przyrostek powinien byc obciety)
            else:
                return cls.next_digit(digit)

    @staticmethod
    def conflicts_with(prev_info, new_info):
        return (prev_info and new_info and
                prev_info.extension == new_info.extension and
                prev_info.date == new_info.date)

    @staticmethod
    def split_digit_and_letter(suffix):
        suffix_match = re.match("(\d*)(\w*)", '' if suffix is None else suffix)
        return suffix_match.groups()

    @staticmethod
    def next_letter(letter):
        if letter == 'z':
            raise Exception("Too many copies")
        return chr(ord(letter) + 1) if letter else 'a'

    @staticmethod
    def next_digit(digit):
        if digit == 9:
            raise Exception("Too many copies")
        return str(int(digit) + 1) if digit else "1"


class Renamer:
    @classmethod
    def rename(cls, directory):
        for (root, dirs, files) in os.walk(directory):
            print("Entering: {}".format(os.path.abspath(root)))

            # przetwarzane obrazki
            images = [os.path.join(root, name) for name in files if IMG_RE.match(name)]
            if not images:
                continue

            # zbierz informacje o obrazkach
            image_infos = cls.collect_image_infos(images)

            # posortuj obrazki w kolejności, rozszerzenie, data, numerek pliku
            image_infos = sorted(image_infos,
                                 key=lambda x: (x.extension, x.date, x.fileNumberField if x.fileNumberField else ''))

            # określ przyrostek pliku
            prev_info = None
            for info in image_infos:
                info.suffix = NamingStrategy.calculate_suffix(prev_info, info)
                prev_info = info

            # odrzuć pliki których nazwa się nie zmieni
            image_infos[:] = [info for info in image_infos if info.filename.lower() != info.new_filename.lower()]

            # zmień nazwy plików
            cls.rename_files(root, image_infos)

    @staticmethod
    def collect_image_infos(images):
        image_infos = []

        # pozbieraj informacje o obrazka przez wywolanie narzedzia exiftool
        for exifJson in JsonUtil.read_exiftool_json(images):
            image_info = ImageInfo.create_from_json(exifJson)
            if image_info.date and MIN_YEAR <= image_info.date.year <= MAX_YEAR:
                image_infos.append(image_info)

        return image_infos

    @classmethod
    def rename_files(cls, root, image_infos):
        # a) na old_<stara_nazwa_pliku>
        for info in image_infos:
            src = os.path.join(root, info.filename)
            dst = os.path.join(root, "old_" + info.filename)
            move_without_overwriting(src, dst)

        # b) na docelową nazwę pliku
        for info in image_infos:
            src = os.path.join(root, "old_" + info.filename)
            dst = os.path.join(root, info.new_filename)
            move_without_overwriting(src, dst)


if __name__ == '__main__':
    Renamer.rename('.')
