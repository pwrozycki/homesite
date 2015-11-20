(function () {
    'use strict';

    angular
        .module('angular')
        .factory('directoryService', directoryService);

    /* @ngInject */
    function directoryService(Restangular, pathsService, collectionPathsService) {
        var service = {
            resolveDirectory: resolveDirectory
        };

        return service;

        //////////

        function resolveDirectory(directoryPath) {
            var pathParam = directoryPath;
            var params = !pathParam ? {root: 'true'} : {path: pathParam};

            return Restangular.one('directories', '').get(params).then(function (directoryJson) {
                var directory = directoryJson.results[0];
                extendFileInformation(directory);
                return directory;
            });
        }

        function extendFileInformation(directory) {
            directory._images = directory.files.filter(function(el) {
                return el.type == 'image';
            });

            directory._videos = directory.files.filter(function(el) {
                return el.type == 'video';
            });

            directory._images.forEach(function(image) {
                image._name = pathsService.basename(image.path);
                image._thumbnailPath = collectionPathsService.thumbnailPath(image.path, image.timestamp);
                image._previewPath = collectionPathsService.previewPath(image.path, image.timestamp);
            });

            directory._videos.forEach(function(video) {
                video._name = pathsService.basename(video.path);
                video._posterPath = collectionPathsService.posterPath(video.path, video.timestamp);
                video._transcodedPath = collectionPathsService.transcodedPath(video.path, video.timestamp);
            });
        }
    }
})();
