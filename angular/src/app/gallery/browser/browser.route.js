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
    function resolveDirectory($stateParams, $state, directoryService, pathsService, $q) {
        var pathFromUri = $stateParams.directoryPath;
        var pathFromUriWithSlashes = pathsService.unescapeSlashes(pathFromUri);
        var directoryPath = decodeURIComponent(pathFromUriWithSlashes);
        return directoryService.resolveDirectory(directoryPath).then(goToMainStateIfNoDirectory);

        function goToMainStateIfNoDirectory(directory) {
            if (!directory) {
                $state.go('main');
                return $q.reject();
            } else {
                return directory;
            }
        }
    }

})();
