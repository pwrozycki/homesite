(function () {
    'use strict';

    angular
        .module('angular')
        .config(routerConfig);

    /* @ngInject */
    function routerConfig($stateProvider) {
        $stateProvider
            .state('main.browser', {
                url: '^/browser/:directoryPath',
                templateUrl: 'app/gallery/browser/browser.html',
                resolve: {
                    directoryPromise: resolveDirectory
                },
                controller: 'BrowserController as browser'
            })
    }

    /* @ngInject */
    function resolveDirectory($stateParams, directoryService) {
        return directoryService.resolveDirectory(decodeURIComponent($stateParams.directoryPath));
    }

})();
