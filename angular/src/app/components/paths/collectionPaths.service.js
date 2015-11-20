(function () {
    'use strict';

    angular
        .module('angular')
        .factory('collectionPathsService', collectionPathsService);

    /* @ngInject */
    function collectionPathsService(pathsService, $q) {
        var collectionInfo = null;

        var ready = $q.defer();

        var service = {
            thumbnailPath: thumbnailPath,
            previewPath: previewPath,
            posterPath: posterPath,
            transcodedPath: transcodedPath,

            ready: ready.promise,
            init: init
        };

        return service;

        ////////////////

        function thumbnailPath(path, timestamp) {
            return pathsService.join(collectionInfo.thumbnails_root, pathWithTimeStamp(path, timestamp)) + ".jpg";
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

