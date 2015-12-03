(function () {
    'use strict';

    angular
        .module('angular')
        .directive('fixedWidget', fixedWidget);

    /* @ngInject */
    function fixedWidget($window, $document) {
        var directive = {
            link: link
        };
        return directive;

        function link(scope, element, attrs) {
            var elementTop = element.offset().top;

            scope.$on('$destroy',
                $document.on('scroll', detectElementVisibilityChange));

            function detectElementVisibilityChange() {
                var scrollTop = angular.element($window).scrollTop();
                if (scrollTop > elementTop) {
                    element.addClass("fixed-widget-fixed");
                } else {
                    element.removeClass("fixed-widget-fixed");
                }
            }
        }
    }
})();

