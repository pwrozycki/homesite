(function () {
    'use strict';

    var FAILURE_LIMIT = 0;
    var THRESHOLD = 200;

    angular
        .module('angular')
        .factory('lazyLoaderService', lazyLoaderService);

    /* @ngInject */
    function lazyLoaderService($window) {
        var jqWindow = angular.element($window);

        var service = {
            notifyVisibleComponents: notifyVisibleComponents
        };

        return service;

        ////////////////

        function notifyVisibleComponents(components) {
            // No components registered - nothing will be found anyway
            if (!components) {
                return;
            }

            var index = binarySearchVisibleComponent(components);

            // iterate over images downwards, beginning with index
            // iterate over images upwards, beginning with index
            getVisibleComponents(components, index, -1).concat(getVisibleComponents(components, index+1, 1)).forEach(
                function (component) {
                    component.onShow();
                });
        }

        function binarySearchVisibleComponent(components) {
            /* Set initial values - lower and upper indices pointing at beginning and end of array */
            var lowerIndex = 0;
            var upperIndex = components.length - 1;
            var testedIndex = 0;

            /* Binary search algorithm - test image in the middle of range: <lowerIndex, upperIndex>.
             Always look for middle value between lowerIndex and upperIndex */
            while (upperIndex > lowerIndex + 1) {
                testedIndex = lowerIndex + Math.floor((upperIndex - lowerIndex) / 2);
                var element = components[testedIndex].element;

                // testedIndex appears to be above viewport
                // there is no use testing smaller indices => lowerIndex = testedIndex
                if (aboveView(element) || leftOfView(element)) {
                    lowerIndex = testedIndex;

                    // testedIndex appears to be below viewport
                    // there is no use testing bigger indices => upperIndex = testedIndex
                } else if (belowTheView(element) || rightToView(element)) {
                    upperIndex = testedIndex;
                } else {
                    break;
                }
            }

            return testedIndex;
        }

        function getVisibleComponents(components, firstElementIndex, step) {
            var componentsInViewport = [];
            var counter = 0;

            // iterate downwards or upwards (depending on step value)
            // show images to be loaded, until failure_limit counter is exceeded
            for (var i = firstElementIndex; i >= 0 && i < components.length; i += step) {
                var component = components[i];
                var element = component.element;

                if (!aboveView(element) && !leftOfView(element) && !belowTheView(element) && !rightToView(element)) {
                    // element in viewport - reset counter
                    counter = 0;
                    componentsInViewport.push(component);
                } else {
                    // to many failures -> stop iterating
                    if (++counter >= FAILURE_LIMIT) {
                        break;
                    }
                }
            }
            return step < 1 ? componentsInViewport.reverse() : componentsInViewport;
        }

        function belowTheView(element) {
            var fold = ($window.innerHeight ? $window.innerHeight : jqWindow.height()) + jqWindow.scrollTop();

            return fold <= element.offset().top - THRESHOLD;
        }

        function rightToView(element) {
            var fold = jqWindow.width() + jqWindow.scrollLeft();

            return fold <= element.offset().left - THRESHOLD;
        }

        function aboveView(element) {
            var fold = jqWindow.scrollTop();

            return fold >= element.offset().top + THRESHOLD + element.height();
        }

        function leftOfView(element) {
            var fold = jqWindow.scrollLeft();

            return fold >= element.offset().left + THRESHOLD + element.width();
        }
    }

})();

