(function () {
    'use strict';

    angular
        .module('angular')
        .factory('preloaderService', preloaderService);

    /* @ngInject */
    function preloaderService($rootScope) {
        var service = {
            preload: preload
        };

        return service;

        ////////////////

        function preload(imageUrls, onSuccessCallback) {
            var nextUrlIndex = 0;
            var imageObject = new Image();
            var successCallback = onSuccessCallback;

            loadNext();

            return stopPreloader;

            function loadNext() {
                if (nextUrlIndex < imageUrls.length) {
                    imageObject.src = imageUrls[nextUrlIndex];
                    imageObject.onload = loadNext;
                    nextUrlIndex += 1;
                } else {
                    stopPreloader();
                    if (successCallback) {
                        $rootScope.$apply(successCallback);
                    }
                }
            }

            function stopPreloader() {
                if (imageObject) {
                    imageObject.onload = null;
                }
                imageObject = null;
            }
        }
    }

})();

