(function () {
    'use strict';

    angular
        .module('angular')
        .config(routerConfig);

    /* @ngInject */
    function routerConfig($stateProvider) {
        $stateProvider
            .state('main', {
                url: '/',
                templateUrl: 'app/gallery/main.html',
                controller: 'MainController as main',
                resolve: {
                    /* @ngInject */
                    appInitialized: function(sessionService, collectionPathsService, $q) {
                        return $q.all([
                            collectionPathsService.ready,
                            sessionService.ready
                        ]);
                    }
                }
            });
    }
})();
