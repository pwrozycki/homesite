#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from copy import deepcopy
from datetime import datetime
from glob import glob
import os
import re
import sys
import cgitb

from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http.response import HttpResponseServerError
from rest_framework import viewsets, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.collectionutils.misc import utc_to_defaulttz
from common.collectionutils.generators import MINIATURE_GENERATORS
from gallery import locations
from common.collectionutils.renameutils import move_without_overwriting, find_or_create_directory, get_mtime_datetime
from gallery.locations import normpath_join, collection_phys_path, COLLECTION_WEB_ROOT, VIDEOS_WEB_ROOT, \
    THUMBNAILS_WEB_ROOT, PREVIEWS_WEB_ROOT
from gallery.models import Directory, Image, ImageGroup, Video, File
from gallery.serializers import DirectorySerializer, ImageSerializer, SubdirectorySerializer, UserSerializer, \
    ImageGroupSerializer, VideoSerializer, FileSerializer, get_polymorphic_serializer


class BadRequestException(Exception):
    def __init__(self, value):
        self.value = value

    def __str(self):
        return repr(self.value)


class FileMoveAPIView(GenericAPIView):
    serializer_class = get_polymorphic_serializer(FileSerializer)
    queryset = File.objects.all()
    resource_name = 'move'

    def post(self, request, *args, **kwargs):
        media_file = self.get_object()
        destination = self.request.data.get('destination', None)
        if destination is None:
            return Response({'reason': 'Required "destination" param is missing'}, status=status.HTTP_400_BAD_REQUEST)

        dst_folder_phys_path = locations.collection_phys_path(destination)
        move_to_trash = locations.web_path_in_trash(destination)
        # destination directory should exists unless media_file is moved to trash (directory tree should be created then)
        if not move_to_trash and not os.path.isdir(dst_folder_phys_path):
            return Response({'reason': 'Invalid destination directory'}, status=status.HTTP_404_NOT_FOUND)

        dst_file_web_path = normpath_join(destination, media_file.name)
        return self._handle_move_request(media_file.path, dst_file_web_path)

    def _add_similar_files_modifications(self, src_file_phys_path, dst_file_phys_path, renames):
        files_with_same_prefix = set(glob(os.path.splitext(src_file_phys_path)[0] + ".*")) - {src_file_phys_path}
        src_dir_phys_path = os.path.dirname(src_file_phys_path)
        dst_dir_phys_path = os.path.dirname(dst_file_phys_path)
        for name in files_with_same_prefix:
            src = os.path.join(src_dir_phys_path, os.path.basename(name))
            dst = os.path.join(dst_dir_phys_path, os.path.basename(name))
            renames.append((src, dst))

    def _move_files_safe(self, src_web_path, dst_web_path):
        """
        Move file in collection from path1 to path2. Also move associated thumbnail and preview file, and any files
        with same prefix in collection folder (mainly RAWS)
        """
        src_file_phys_path = locations.collection_phys_path(src_web_path)
        dst_file_phys_path = locations.collection_phys_path(dst_web_path)

        # create list of modifications files will be moved in loop at the end of method
        renames = [(src_file_phys_path, dst_file_phys_path)]

        # query generators and add all generated miniatures to renames
        for generator in MINIATURE_GENERATORS:
            if generator.will_output_file(src_web_path):
                src_miniature_phys_path = generator.miniature_phys_path(src_file_phys_path)
                dst_miniature_phys_path = self._calculate_dst_path_after_move(src_web_path, dst_web_path,
                                                                              src_miniature_phys_path)
                renames.append((src_miniature_phys_path, dst_miniature_phys_path))

        # add move of "other files in group" in collection folder
        self._add_similar_files_modifications(src_file_phys_path, dst_file_phys_path, renames)

        # move files in batch
        # TODO: rollback changes (move files back to their original positions) on error
        for (src, dst) in renames:
            move_without_overwriting(src, dst,
                                     # allow creating destination folders only in trash
                                     create_destination_dir=locations.web_path_in_trash(dst_web_path))

    def _calculate_dst_path_after_move(self, src_web_path, dst_web_path, src_miniature_phys_path):
        src_dir_web_path = os.path.dirname(src_web_path)
        dst_dir_web_path = os.path.dirname(dst_web_path)
        src_dir_pattern = re.escape(src_dir_web_path) + '$'
        src_miniature_dir_phys_path, src_miniature_filename = os.path.split(src_miniature_phys_path)
        dst_miniature_dir_phys_path = os.path.join(re.sub(src_dir_pattern, "", src_miniature_dir_phys_path),
                                                   dst_dir_web_path)
        return os.path.join(dst_miniature_dir_phys_path, src_miniature_filename)

    def _move_files(self, src_web_path, dst_web_path):
        src_phys_path = locations.collection_phys_path(src_web_path)

        if not os.path.isfile(src_phys_path):
            raise BadRequestException("Source file doesn't exist: " + src_phys_path)

        self._move_files_safe(src_web_path, dst_web_path)

    @staticmethod
    def _create_directories_in_chain(directory):
        parent_paths = [directory]
        parent = os.path.dirname(directory)
        while len(parent) > 0:
            parent_paths.append(parent)
            parent = os.path.dirname(parent)

        previous_parent = None
        for path in reversed(parent_paths):
            previous_parent = find_or_create_directory(path, previous_parent)

    def _update_database_after_move(self, src_file_web_path, dst_file_web_path):
        try:
            media_file = File.objects.get(
                name=(os.path.basename(src_file_web_path)),
                directory__path=os.path.dirname(src_file_web_path))

            # create parent directory objects
            dst_dir_web_path = os.path.dirname(dst_file_web_path)
            self._create_directories_in_chain(dst_dir_web_path)

            # if media_file is moved to trash save current timestamp as trash_time
            # otherwise unset trash_time
            move_to_trash = locations.web_path_in_trash(dst_file_web_path)
            if move_to_trash:
                now = utc_to_defaulttz(datetime.utcnow())
                trash_time = now
            else:
                trash_time = None

            # parent directory should exist
            new_directory = Directory.objects.get(path=dst_dir_web_path)

            # update directory modification times
            self._update_directory_mtime(new_directory)
            self._update_directory_mtime(media_file.directory)

            media_file.directory = new_directory
            media_file.trash_time = trash_time
            media_file.save()

        except (File.DoesNotExist, Directory.DoesNotExist):
            raise BadRequestException("Database object doesn't exist: (name={0})".format(src_file_web_path))

    @staticmethod
    def _update_directory_mtime(new_directory):
        new_directory.modification_time = get_mtime_datetime(collection_phys_path(new_directory.path))
        new_directory.save()

    @transaction.atomic
    def _move_file(self, src_file_web_path, dst_file_web_path):
        self._move_files(src_file_web_path, dst_file_web_path)
        self._update_database_after_move(src_file_web_path, dst_file_web_path)

    def _handle_move_request(self, src_web_path, dst_web_path):
        try:
            src_web_path = os.path.normpath(src_web_path)

            self._move_file(src_web_path, dst_web_path)
            return Response()
        except BadRequestException:
            return Response({'traceback': self.get_traceback_string()}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return HttpResponseServerError(self.get_traceback_string())

    @staticmethod
    def get_traceback_string():
        exc_info = sys.exc_info()
        return cgitb.html(exc_info)


class FilterByIdsMixin(object):
    IDS_PARAM = 'ids[]'

    def get_queryset(self):
        queryset = super().get_queryset()

        ids_param_list = self.request.query_params.getlist(FilterByIdsMixin.IDS_PARAM, None)
        if ids_param_list:
            return queryset.filter(pk__in=ids_param_list)
        else:
            return queryset


class SubdirectoryViewSet(FilterByIdsMixin, viewsets.ModelViewSet):
    queryset = Directory.objects.all()
    serializer_class = SubdirectorySerializer
    filter_fields = ('path', 'parent', 'shared')
    resource_name = 'subdirectory'

    PATH_LIKE_PARAM = 'path_like'
    # Trash will match a/Trash, Trash
    PATH_PATTERN_REPLACEMENTS = [(r'\*', r'[^/]*'),
                                 (r'\|', r'.*?/')]

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = self._filter_out_unauthorized(queryset)
        queryset = self._filter_by_path_param(queryset)

        if 'root' in self.request.query_params:
            queryset = queryset.filter(parent__isnull=True)

        return queryset

    def _filter_by_path_param(self, queryset):
        """
        For path_like query parameter generate regex pattern filtering out non matching records.
        """
        path_like_param = self.request.query_params.get(self.PATH_LIKE_PARAM, None)
        if path_like_param:
            path_exp = self._get_regex_pattern(self.PATH_PATTERN_REPLACEMENTS, path_like_param)
            path_exp = '(?i)^(.*?/)*' + path_exp
            queryset = queryset.filter(path__regex=path_exp)

        return queryset

    def _get_regex_pattern(self, replacements, str):
        replacements = deepcopy(replacements)
        if replacements:
            (pattern, replacement) = replacements.pop(0)
            return replacement.join([self._get_regex_pattern(replacements, x) for x in re.split(pattern, str)])
        else:
            return re.escape(str)

    def _filter_out_unauthorized(self, queryset):
        """
        If user not authenticated return only shared directories and their descendants
        """
        if not self.request.user.is_authenticated():
            shared_dirs = Directory.objects.filter(shared=True).values_list('path', flat=True)
            if not shared_dirs:
                queryset = queryset.none()
            else:
                is_child_of_shared = self.is_descendant_of_path(shared_dirs)
                queryset = queryset.filter(is_child_of_shared | Q(shared=True))

        return queryset

    def is_descendant_of_path(self, shared_paths):
        """
        Returns expression matching paths that are children of paths listed in shared_paths
        """
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


class VideoViewSet(FilterByIdsMixin, viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    filter_fields = ('name', 'directory')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CollectionInfoView(APIView):
    resource_name = 'collectionInfo'

    def get(self, request):
        return Response({
            'id': 1,
            'videos_root': VIDEOS_WEB_ROOT,
            'thumbnails_root': THUMBNAILS_WEB_ROOT,
            'previews_root': PREVIEWS_WEB_ROOT,
            'originals_root': COLLECTION_WEB_ROOT
        })


class ImageGroupView(APIView):
    resource_name = 'imageGroup'

    def get(self, request):
        directory_id = request.query_params.get('directoryId', None)
        if not directory_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        image_groups = ImageGroup.objects.extra(
            # restrict image groups that have images from different directories
            # (excluding the ones rooted in Trash)
            where=['''
                (select count(distinct(gd.id))
                from gallery_file gi
                join gallery_directory gd         on gi.directory_id = gd.id
                where gallery_imagegroup.id = gi.image_group_id and
                      not (gd.path  like 'Trash/%%' or gd.path = 'Trash')) > 1
            ''']
        ).filter(images__directory__pk=directory_id)

        if image_groups.count():
            return Response(ImageGroupSerializer(image_groups.all(), many=True).data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class SessionView(APIView):
    permission_classes = [AllowAny]
    resource_name = 'session'

    def get(self, request, *args, **kwargs):
        # Get the current user
        if request.user.is_authenticated():
            return Response({'user_id': request.user.id})
        return Response({'user_id': None})

    def post(self, request, *args, **kwargs):
        # Login
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return Response({'success': True, 'user_id': user.id})

        return Response({'success': False})

    def delete(self, request, *args, **kwargs):
        # Logout
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
