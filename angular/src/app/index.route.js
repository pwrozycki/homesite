(function () {
    'use strict';

    angular
        .module('angular')
        .config(routerConfig);

    /* @ngInject */
    function routerConfig($stateProvider, $urlRouterProvider) {
        $stateProvider
            .state('gallery', {
                url: '/',
                templateUrl: 'app/gallery/templates/gallery.html',
                controller: 'GalleryController',
                controllerAs: 'gal'
            })
            .state('gallery.directory', {
                url: 'directory/:directoryPath',
                templateUrl: 'app/gallery/templates/directory.html',
                resolve: {
                    directoryObj: directoryObj
                },
                controller: "DirectoryController as dir"
            });

        $urlRouterProvider.otherwise('/');

    }

    /* @ngInject */
    function directoryObj($stateParams, directoryService) {
        return directoryService.resolveDirectory(decodeURIComponent($stateParams.directoryPath));
    }

})();
