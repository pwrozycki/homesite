(function () {
    'use strict';

    angular
        .module('angular')
        .factory('collectionPathsService', collectionPathsService);

    /* @ngInject */
    function collectionPathsService(pathsService, $q, collectionPathsConstants) {
        var collectionInfo = null;

        var ready = $q.defer();

        var service = {
            thumbnailPath: thumbnailPath,
            previewPath: previewPath,
            originalJpegPath: originalJpegPath,
            posterPath: posterPath,
            transcodedPath: transcodedPath,

            pathInTrash: pathInTrash,
            pathOutsideTrash: pathOutsideTrash,
            isPathInTrash: isPathInTrash,

            ready: ready.promise,
            init: init
        };

        return service;

        ////////////////

        function pathInTrash(path) {
            if (! isPathInTrash(path)) {
                return pathsService.join(collectionPathsConstants.TRASH, path);
            } else {
                return path;
            }

        }

        function pathOutsideTrash(path) {
            if (isPathInTrash(path)) {
                return path.replace(new RegExp('^(/)?' + collectionPathsConstants.TRASH + '/?'), '$1');
            } else {
                return path;
            }
        }

        function isPathInTrash(path) {
            return !!path.match(new RegExp('^/?' + collectionPathsConstants.TRASH))
        }

        function thumbnailPath(path, timestamp) {
            return pathsService.join(collectionInfo.thumbnails_root, pathWithTimeStamp(path, timestamp)) + ".jpg";
        }

        function originalJpegPath(path) {
            return pathsService.join(collectionInfo.originals_root, path);
        }

        function previewPath(path, timestamp) {
            return pathsService.join(collectionInfo.previews_root, pathWithTimeStamp(path, timestamp)) + ".jpg";
        }

        function posterPath(path, timestamp) {
            return pathsService.join(collectionInfo.videos_root, pathWithTimeStamp(path, timestamp)) + ".jpg";
        }

        function transcodedPath(path, timestamp) {
            return pathsService.join(collectionInfo.videos_root, pathWithTimeStamp(path, timestamp)) + ".mp4";
        }

        function pathWithTimeStamp(path, timestamp) {
            return path + "_" + timestamp;
        }

        function init(info) {
            collectionInfo = info;
            ready.resolve();
        }
    }

})();

