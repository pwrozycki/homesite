(function () {
    'use strict';

    angular
        .module('homeGallery')
        .factory('directoryService', directoryService);

    /* @ngInject */
    function directoryService(Restangular) {
        var service = {
            resolveDirectory: resolveDirectory
        };

        return service;

        //////////

        /* @ngInject */
        function resolveDirectory(directoryPath) {
            var pathParam = directoryPath;
            var params = !pathParam ? {root: 'true'} : {path: pathParam};
            return Restangular.one('directories', '').get(params).then(function (directory) {
                return directory;
            });
        }

    }
})();
