(function () {
    'use strict';

    var IMAGE_EXT = 'jpg';
    var MOVIE_EXT = 'mp4';

    var collectionInfo = null;

    angular
        .module('angular').
        factory('collectionService', collectionService).

        run(function (Restangular, $log) {
            Restangular.one('collectionInfos', 1).get().then(function (info) {
                collectionInfo = info;
            });
        });

    /* @ngInject */
    function collectionService(pathsService) {
        var service = {

        };

        return service;

        ////////

        function thumbnailPath(directoryPath, file) {
            pathsService.join(directoryPath, image.path)
        }

        function pathWithTimestamp(file) {
            return image.path + "_" + image.timestamp
        }

        function extensionForType(file) {

        }
    }
})();

