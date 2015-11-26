(function () {
    'use strict';

    angular
        .module('angular')
        .factory('fileService', fileService);

    /* @ngInject */
    function fileService(Restangular, collectionPathsService, pathsService) {
        var service = {
            move: move,
            moveToTrash: moveToTrash,
            moveFromTrash: moveFromTrash,
            isImageInTrash: isImageInTrash
        };

        return service;

        ////////////////

        function isImageInTrash(file) {
            return collectionPathsService.isPathInTrash(file.path);
        }

        function moveFromTrash(file) {
            return move(file, collectionPathsService.pathOutsideTrash(pathsService.dirname(file.path)));
        }

        function moveToTrash(file) {
            return move(file, collectionPathsService.pathInTrash(pathsService.dirname(file.path)));
        }

        function move(file, destination) {
            return Restangular.one('files', file.id).post('move', { destination: destination });
        }
    }

})();

