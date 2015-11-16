(function () {
    'use strict';

    angular
        .module('angular')
        .factory('collectionPathsService', collectionPathsService);

    /* @ngInject */
    function collectionPathsService(pathsService) {
        var collectionInfo = null;

        var service = {
            thumbnailPath: thumbnailPath,
            _setCollectionInfo: setCollectionInfo
        };

        return service;

        ////////////////

        function thumbnailPath(path, timestamp) {
            return pathsService.join(collectionInfo.thumbnails_root, pathWithTimeStamp(path, timestamp));
        }

        function pathWithTimeStamp(path, timestamp) {
            return path + "_" + timestamp + ".jpg";
        }

        function setCollectionInfo(info) {
            collectionInfo = info;
        }
    }

})();

