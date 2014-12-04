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
from django.db.models import Q
from django.http.response import HttpResponseServerError
import resource
from rest_framework import viewsets, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
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


def trash_or_revert_image(path):
    try:
        src_image_web_path = os.path.normpath(path)

        if not re.search(TRASH_DIRECTORY_REGEXP, path):
            dst_image_web_path = os.path.join(locations.TRASH_DIR_NAME, path)
        else:
            dst_image_web_path = re.sub(TRASH_DIRECTORY_REGEXP, '', src_image_web_path)

        move_image(src_image_web_path, dst_image_web_path)
        return Response()
    except BadRequestException:
        return Response({'traceback': get_traceback_string()}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return HttpResponseServerError(get_traceback_string())


class ImageModificationAPIView(GenericAPIView):
    serializer_class = ImageSerializer
    model = Image

    def post(self, request, *args, **kwargs):
        image = self.get_object()

        return self.handle_post(image)


class TrashImageView(ImageModificationAPIView):
    def handle_post(self, image):
        return trash_or_revert_image(image.path)


class RevertImageView(ImageModificationAPIView):
    def handle_post(self, image):
        return trash_or_revert_image(image.path)


class FilterByIdsMixin(object):
    IDS_PARAM = 'ids[]'

    def get_queryset(self):
        queryset = super(FilterByIdsMixin, self).get_queryset()
        if FilterByIdsMixin.IDS_PARAM in self.request.QUERY_PARAMS:
            ids_param_list = self.request.QUERY_PARAMS.getlist(FilterByIdsMixin.IDS_PARAM)
            return queryset.filter(pk__in=ids_param_list)
        else:
            return queryset


class SubdirectoryViewSet(FilterByIdsMixin, viewsets.ModelViewSet):
    queryset = Directory.objects.all()
    serializer_class = SubdirectorySerializer
    filter_fields = ('path', 'parent', 'shared')
    resource_name = 'subdirectory'

    def get_queryset(self):
        queryset = super(SubdirectoryViewSet, self).get_queryset()

        # if user not authenticated return only shared directories and their descendants
        if not self.request.user.is_authenticated():
            shared_dirs = Directory.objects.filter(shared=True).values_list('path', flat=True)
            if not shared_dirs:
                queryset = queryset.none()
            else:
                is_child_of_shared = self.is_descendant_of_path(shared_dirs)
                queryset = queryset.filter(is_child_of_shared | Q(shared=True))

        # return only root directory
        if 'root' in self.request.QUERY_PARAMS:
            return queryset.filter(parent__isnull=True)
        else:
            return queryset

    def is_descendant_of_path(self, shared_paths):
        """ Returns expression matching paths that are children of paths listed in shared_paths  """
        exp = None
        for path in shared_paths:
            new_exp = Q(path__startswith=path + '/')
            if exp:
                exp = exp | new_exp
            else:
                exp = new_exp
        return exp


class DirectoryViewSet(SubdirectoryViewSet):
    serializer_class = DirectorySerializer
    resource_name = 'directory'


class ImageViewSet(FilterByIdsMixin, viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    filter_fields = ('name', 'directory')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    model = User
    serializer_class = UserSerializer


class CollectionInfoView(APIView):
    resource_name = 'collectionInfo'

    def get(self, request):
        return Response({
            'id': 1,
            'thumbnailsRoot': locations.thumbnail_web_path(''),
            'previewsRoot': locations.preview_web_path(''),
            'originalsRoot': locations.original_web_path('')
        })


class SessionView(APIView):
    permission_classes = [AllowAny]

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