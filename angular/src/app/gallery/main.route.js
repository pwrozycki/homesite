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
                controller: 'MainController as main'
            });
    }
})();
