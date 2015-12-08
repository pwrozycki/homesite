(function () {
    'use strict';

    angular
        .module('angular')
        .directive('renderOnHover', renderOnHover);

    /* @ngInject */
    function renderOnHover() {
        var directive = {
            transclude: true,
            link: link,
            template: '<div ng-if="hover""><div ng-transclude></div></div>'
        };
        return directive;

        function link(scope, element) {
            element.on('mouseenter', onEnter);
            element.on('mouseleave', onLeave);

            scope.$on('$destroy', function(){
                element.off('mouseEnter', onEnter);
                element.off('mouseLeave', onLeave);
            });

            function onEnter() {
                scope.hover = true;
            }

            function onLeave() {
                scope.hover = false;
            }
        }
    }
})();

