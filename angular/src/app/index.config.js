(function () {
    'use strict';

    angular
        .module('homeGallery')
        .config(config);

    /** @ngInject */
    function config($logProvider, RestangularProvider, _) {

        RestangularProvider.setBaseUrl('gallery/api');
        RestangularProvider.setDefaultHttpFields({
            withCredentials: true
        });

        // 1) Adapt to ember REST API quirks
        // 1.a) simulate original DJANGO JSON
        RestangularProvider.addResponseInterceptor(function(element/*, operation, what, url */) {
            var meta = null;
            var content = null;
            _.forIn(element, function(value, key) {
                if (key === 'meta') {
                    meta = value;
                } else {
                    content = value;
                }
            });

            if (meta) {
                var metaCopy = angular.copy(meta);
                metaCopy.results = content;
                return metaCopy;
            } else {
                return content;
            }
        });

        RestangularProvider.addFullRequestInterceptor(function(element, operation, what, url, headers) {
            // 2) add CSRFTOKEN header to every request
            var $cookies = angular.injector(['ngCookies']).get('$cookies');
            var csrftoken = $cookies.get('csrftoken');
            headers['X-CSRFTOKEN'] = csrftoken;

            // 1.b) wrap payload in element name
            var wrappedElement = {};
            wrappedElement[what] = element;

            return {
                element: wrappedElement,
                headers: headers
            }
        });

        // Enable log
        $logProvider.debugEnabled(true);
    }

})();
