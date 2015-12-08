(function () {
    'use strict';

    angular
        .module('angular')
        .directive('aDisabled', aDisabled);

    /* @ngInject */
    function aDisabled() {
        var directive = {
            restrict: 'A',
            link: link
        };
        return directive;

        function link(scope, element, attrs) {
            attrs.$observe('aDisabled', function(value) {
                if (scope.$eval(value)) {
                    element.attr('disabled', 'disabled');
                    element.on('click', preventDefault);

                    scope.$on('$destroy', function() {
                        element.off('click', preventDefault);
                    })
                } else {
                    element.off('click', preventDefault);
                    element.attr('disabled', null);
                }
            });
        }

        function preventDefault(event) {
            event.preventDefault();
        }
    }
})();

