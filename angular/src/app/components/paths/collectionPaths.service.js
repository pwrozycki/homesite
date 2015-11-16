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

            ready: ready.promise,
            init: init
        };

        return service;

        ////////////////

        function thumbnailPath(path, timestamp) {
            return pathsService.join(collectionInfo.thumbnails_root, pathWithTimeStamp(path, timestamp));
        }

        function pathWithTimeStamp(path, timestamp) {
            return path + "_" + timestamp + ".jpg";
        }

        function init(info) {
            collectionInfo = info;
            ready.resolve();
        }
    }

})();

