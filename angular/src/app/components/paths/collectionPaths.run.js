(function () {
    'use strict';
    angular
        .module('angular')
        .run(runCollectionPaths);

    /* @ngInject */
    function runCollectionPaths(Restangular, collectionPathsService) {
        Restangular.one('collectionInfos', 1).get().then(function(collectionInfo) {
            collectionPathsService.init(collectionInfo);
        });
    }

})();

