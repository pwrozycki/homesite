#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import json
import os
import re
import fnmatch

from django.http import Http404
from django.http.response import HttpResponseServerError, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST
from rest_framework import viewsets
from common import debugtool

from gallery import locations
from common.collectionutils.renameutils import move_without_overwriting
from gallery.models import Directory, Image
from gallery.serializers import DirectorySerializer, ImageSerializer

TRASH_DIRECTORY_REGEXP = r'^/?{}/'.format(locations.TRASH_DIRECTORY)
JPG_REGEXP = re.compile(fnmatch.translate("*.JPG"), re.IGNORECASE)


def list_dir(request, web_path):
    collection_dir = locations.COLLECTION_PHYS_ROOT
    if web_path:
        collection_dir = locations.collection_phys_path(web_path)

    if not os.path.exists(collection_dir):
        raise Http404()

    dir_listing = [x for x in sorted(os.listdir(collection_dir))]

    subdirs = [os.path.join(web_path, x) for x in dir_listing if
               not x.startswith('.') and os.path.isdir(os.path.join(collection_dir, x))]
    images = [os.path.join(web_path, x) for x in dir_listing if JPG_REGEXP.match(os.path.basename(x))]

    path = os.path.normpath(web_path)
    dirs = []
    while path not in ('/', '.', ''):
        (dir_name, base) = os.path.split(path)
        dirs.append({'name': base, 'path': path})
        path = dir_name

    dirs.append({'name': 'ROOT', 'path': path})
    dirs.reverse()

    directory_contents = {
        'images': [{'path': image,
                    'preview': locations.preview_web_path(image),
                    'thumbnail': locations.thumbnail_web_path(image),
                    'description': os.path.basename(image),
                   } for image in images],
        'subdirs': [{'path': path,
                     'name': os.path.basename(path),
                    } for path in subdirs],
        'directories': dirs
    }

    json_result = json.dumps(directory_contents)

    callback = request.GET.get('callback', None)
    if callback:
        jsonp_result = '{0}({1})'.format(callback, json_result)
        return HttpResponse(jsonp_result, mimetype="text/javascript")

    return HttpResponse(json_result, mimetype="application/json")


def browse(request, dir_path):
    collection_dir = locations.COLLECTION_PHYS_ROOT
    if dir_path:
        collection_dir = locations.collection_phys_path(dir_path)

    if not os.path.exists(collection_dir):
        raise Http404()

    return render(request, "browse.html", {'directory': dir_path})


def _move_files(path1, path2):
    original_src_path = locations.collection_phys_path(path1)
    original_dst_path = locations.collection_phys_path(path2)
    move_without_overwriting(original_src_path, original_dst_path, create_destination_dir=True)

    preview_src_path = locations.preview_phys_path(path1)
    preview_dst_path = locations.preview_phys_path(path2)
    move_without_overwriting(preview_src_path, preview_dst_path, create_destination_dir=True)

    thumbnail_src_path = locations.thumbnail_phys_path(path1)
    thumbnail_dst_path = locations.thumbnail_phys_path(path2)
    move_without_overwriting(thumbnail_src_path, thumbnail_dst_path, create_destination_dir=True)


def _move_image_groups(src_web_path, dst_web_path):
    src_phys_path = locations.collection_phys_path(src_web_path)
    if not os.path.isfile(src_phys_path):
        return HttpResponseBadRequest()
    try:
        _move_files(src_web_path, dst_web_path)

        return HttpResponse()

    except Exception as a:
        return HttpResponseServerError()


def _remove_empty_directories(root):
    for (root, directories, files) in os.walk(root, topdown=False):
        for directory in directories:
            joined_path = os.path.join(root, directory)
            if not os.listdir(joined_path):
                os.rmdir(joined_path)


@require_POST
def delete_image(request, path):
    src_web_path = os.path.normpath(path)
    dst_web_path = os.path.join(locations.TRASH_DIRECTORY, path)

    if re.search(TRASH_DIRECTORY_REGEXP, path):
        return HttpResponseBadRequest()

    return _move_image_groups(src_web_path, dst_web_path)


@require_POST
def revert_image(request, path):
    src_web_path = os.path.normpath(path)
    dst_web_path = re.sub(TRASH_DIRECTORY_REGEXP, '', src_web_path)

    if not re.search(TRASH_DIRECTORY_REGEXP, path):
        return HttpResponseBadRequest()

    response = _move_image_groups(src_web_path, dst_web_path)

    thrash_root_phys_path = locations.collection_phys_path(locations.TRASH_DIRECTORY)
    _remove_empty_directories(thrash_root_phys_path)

    return response


class FilterByIdsMixin(object):
    IDS_PARAM = 'ids[]'

    def get_queryset(self):
        queryset = super(FilterByIdsMixin, self).get_queryset()
        if FilterByIdsMixin.IDS_PARAM in self.request.QUERY_PARAMS:
            ids_param_list = self.request.QUERY_PARAMS.getlist(FilterByIdsMixin.IDS_PARAM)
            return queryset.filter(pk__in=ids_param_list)
        else:
            return queryset


class DirectoryViewSet(FilterByIdsMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Directory.objects.all()
    serializer_class = DirectorySerializer
    filter_fields = ('path', 'parent')

    def get_queryset(self):
        queryset = super(DirectoryViewSet, self).get_queryset()
        if 'root' in self.request.QUERY_PARAMS:
            return queryset.filter(parent__isnull=True)
        else:
            return queryset


class ImageViewSet(FilterByIdsMixin, viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    filter_fields = ('name', 'directory')