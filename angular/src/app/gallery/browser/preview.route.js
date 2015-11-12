(function () {
    'use strict';

    angular
        .module('angular')
        .config(routerConfig);

    /* @ngInject */
    function routerConfig($stateProvider) {
        $stateProvider
            .state('main.browser.preview', {
                url: '/preview/:imageName',
                templateUrl: 'app/gallery/browser/preview.html',
                controller: "PreviewController as preview",
                resolve: {
                    /* @ngInject */
                    imagePromise: resolveImage
                }
            });

        function resolveImage($stateParams, directoryPromise, _) {
            var imageName = decodeURIComponent($stateParams.imageName);
            return _.find(directoryPromise.files, function (image) {
                return image.path.endsWith(imageName);
            });
        }
    }

})();
