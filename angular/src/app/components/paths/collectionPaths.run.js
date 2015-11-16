(function () {
    'use strict';
    angular
        .module('angular')
        .run(getCollectionPaths);

    /* @ngInject */
    function getCollectionPaths(Restangular, collectionPathsService) {
        Restangular.one('collectionInfos', 1).get().then(function(collectionInfo) {
            collectionPathsService._setCollectionInfo(collectionInfo);
        });
    }

})();

