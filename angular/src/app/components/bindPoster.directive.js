(function () {
    'use strict';

    angular
        .module('angular')
        .directive('bindPoster', bindPoster);

    /* @ngInject */
    function bindPoster() {
        var directive = {
            priority: 99,
            link: link,
            restrict: 'A'
        };

        return directive;

        function link(scope, element, attrs) {
            attrs.$observe('bindPoster', function(value) {
                if (value) {
                    attrs.$set('poster', value);
                }
            });
        }
    }
})();

