#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import os
import re
import fnmatch
import sys
import cgitb
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User

from django.db import transaction
from django.http.response import HttpResponseServerError, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from gallery import locations
from common.collectionutils.renameutils import move_without_overwriting, find_or_create_directory
from gallery.models import Directory, Image
from gallery.serializers import DirectorySerializer, ImageSerializer, SubdirectorySerializer, UserSerializer


TRASH_DIRECTORY_REGEXP = r'^/?{}/'.format(locations.TRASH_DIR_NAME)
JPG_REGEXP = re.compile(fnmatch.translate("*.JPG"), re.IGNORECASE)


def get_traceback_string():
    exc_info = sys.exc_info()
    return cgitb.html(exc_info)


class BadRequestException(Exception):
    def __init__(self, value):
        self.value = value

    def __str(self):
        return repr(self.value)


def _move_image_groups_safe(path1, path2):
    original_src_path = locations.collection_phys_path(path1)
    original_dst_path = locations.collection_phys_path(path2)
    move_without_overwriting(original_src_path, original_dst_path, create_destination_dir=True)

    preview_src_path = locations.preview_phys_path(path1)
    preview_dst_path = locations.preview_phys_path(path2)
    move_without_overwriting(preview_src_path, preview_dst_path, create_destination_dir=True)

    thumbnail_src_path = locations.thumbnail_phys_path(path1)
    thumbnail_dst_path = locations.thumbnail_phys_path(path2)
    move_without_overwriting(thumbnail_src_path, thumbnail_dst_path, create_destination_dir=True)


def _move_image_groups(src_web_path, dst_web_path, empty_orphaned_directories=False):
    src_phys_path = locations.collection_phys_path(src_web_path)

    if not os.path.isfile(src_phys_path):
        raise BadRequestException("Source file doesn't exist: " + src_phys_path)

    _move_image_groups_safe(src_web_path, dst_web_path)

    if empty_orphaned_directories:
        thrash_root_phys_path = locations.collection_phys_path(locations.TRASH_DIR_NAME)
        _remove_empty_directories(thrash_root_phys_path)


def _remove_empty_directories(root):
    for (root, directories, files) in os.walk(root, topdown=False):
        for directory in directories:
            joined_path = os.path.join(root, directory)
            if not os.listdir(joined_path):
                os.rmdir(joined_path)


def _create_directories_in_chain(directory):
    parent_paths = [directory]
    parent = os.path.dirname(directory)
    while len(parent) > 0:
        parent_paths.append(parent)
        parent = os.path.dirname(parent)

    previous_parent = None
    for path in reversed(parent_paths):
        previous_parent = find_or_create_directory(path, previous_parent)


def _update_database_after_move(src_image_web_path, dst_image_web_path):
    try:
        image = Image.objects.get(
            name=(os.path.basename(src_image_web_path)),
            directory__path=os.path.dirname(src_image_web_path))

        # create parent directory objects
        dst_dir_web_path = os.path.dirname(dst_image_web_path)
        _create_directories_in_chain(dst_dir_web_path)

        # parent directory should exist
        new_directory = Directory.objects.get(path=dst_dir_web_path)
        image.directory = new_directory
        image.save()

    except (Image.DoesNotExist, Directory.DoesNotExist):
        raise BadRequestException("Database object doesn't exist: (name={0})".format(src_image_web_path))


@transaction.atomic
def move_image(src_image_web_path, dst_image_web_path, empty_orphaned_directories=False):
    _move_image_groups(src_image_web_path, dst_image_web_path, empty_orphaned_directories)
    _update_database_after_move(src_image_web_path, dst_image_web_path)


@require_POST
def delete_image(request, path):
    if re.search(TRASH_DIRECTORY_REGEXP, path):
        return HttpResponseBadRequest("Image is in Trash already.")

    try:
        src_image_web_path = os.path.normpath(path)
        dst_image_web_path = os.path.join(locations.TRASH_DIR_NAME, path)
        move_image(src_image_web_path, dst_image_web_path)
        return HttpResponse()
    except BadRequestException:
        return HttpResponseBadRequest(get_traceback_string())
    except Exception:
        return HttpResponseServerError(get_traceback_string())


@require_POST
def revert_image(request, path):
    if not re.search(TRASH_DIRECTORY_REGEXP, path):
        return HttpResponseBadRequest("Image should be in Trash.")

    try:
        src_image_web_path = os.path.normpath(path)
        dst_image_web_path = re.sub(TRASH_DIRECTORY_REGEXP, '', src_image_web_path)
        move_image(src_image_web_path, dst_image_web_path)
        return HttpResponse()
    except BadRequestException:
        return HttpResponseBadRequest(get_traceback_string())
    except Exception:
        return HttpResponseServerError(get_traceback_string())


class FilterByIdsMixin(object):
    IDS_PARAM = 'ids[]'

    def get_queryset(self):
        queryset = super(FilterByIdsMixin, self).get_queryset()
        if FilterByIdsMixin.IDS_PARAM in self.request.QUERY_PARAMS:
            ids_param_list = self.request.QUERY_PARAMS.getlist(FilterByIdsMixin.IDS_PARAM)
            return queryset.filter(pk__in=ids_param_list)
        else:
            return queryset


class DirectoryViewSet(FilterByIdsMixin, viewsets.ModelViewSet):
    queryset = Directory.objects.all()
    serializer_class = DirectorySerializer
    filter_fields = ('path', 'parent')

    def get_queryset(self):
        queryset = super(DirectoryViewSet, self).get_queryset()
        if 'root' in self.request.QUERY_PARAMS:
            return queryset.filter(parent__isnull=True)
        else:
            return queryset


class SubdirectoryViewSet(FilterByIdsMixin, viewsets.ModelViewSet):
    queryset = Directory.objects.all()
    serializer_class = SubdirectorySerializer
    filter_fields = ('path', 'parent')
    resource_name = 'subdirectory'


class ImageViewSet(FilterByIdsMixin, viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    filter_fields = ('name', 'directory')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    model = User
    serializer_class = UserSerializer


class SessionView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the current user
        if request.user.is_authenticated():
            return Response({'user_id': request.user.id})
        return Response({'user_id': None})

    def post(self, request, *args, **kwargs):
        # Login
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return Response({'success': True, 'user_id': user.id})

        return Response({'success': False})

    def delete(self, request, *args, **kwargs):
        # Logout
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)