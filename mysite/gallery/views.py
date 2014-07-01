#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import json
import os
import re
import fnmatch

from django.http import Http404, HttpResponse
from django.http.response import HttpResponseServerError, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST

from gallery import locations
from common.collectionutils.renameutils import move_without_overwriting


JPG_RE = re.compile(fnmatch.translate("*.JPG"), re.IGNORECASE)


def list_dir(request, web_path):
    collection_dir = locations.COLLECTION_PHYS_ROOT
    if web_path:
        collection_dir = os.path.abspath(locations.collection_phys_path(web_path))

    if not os.path.exists(collection_dir):
        raise Http404()

    dir_listing = [x for x in sorted(os.listdir(collection_dir))]

    subdirs = [os.path.join(web_path, x) for x in dir_listing if
               not x.startswith('.') and os.path.isdir(os.path.join(collection_dir, x))]
    images = [os.path.join(web_path, x) for x in dir_listing if JPG_RE.match(os.path.basename(x))]

    path = os.path.normpath(web_path)
    dirs = []
    while path not in ('/', '.', ''):
        (dir_name, base) = os.path.split(path)
        dirs.append({'name': base, 'path': path})
        path = dir_name

    dirs.append({'name': 'ROOT', 'path': path})
    dirs.reverse()

    directory_contents = {
        'images': [{'preview': locations.preview_web_path(image),
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
        collection_dir = os.path.abspath(locations.collection_phys_path(dir_path))

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


def _move_image_groups(dst_web_path, src_web_path):
    src_phys_path = os.path.abspath(locations.collection_phys_path(src_web_path))
    if not os.path.isfile(src_phys_path):
        return HttpResponseBadRequest()
    try:
        _move_files(src_web_path, dst_web_path)

        return HttpResponse()

    except Exception as a:
        return HttpResponseServerError()


@require_POST
def delete_image(request, path):
    dst_web_path = os.path.join(locations.THRASH_DIRECTORY, path)
    src_web_path = path

    import common.debugtool;common.debugtool.settrace()

    return _move_image_groups(dst_web_path, src_web_path)

@require_POST
def revert_image(request, path):
    norm_path = os.path.normpath(path)
    # TODO: dokończyć

