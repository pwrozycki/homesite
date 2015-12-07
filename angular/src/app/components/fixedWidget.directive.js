(function () {
    'use strict';

    angular
        .module('angular')
        .directive('fixedWidget', fixedWidget);

    /* @ngInject */
    function fixedWidget($window, $document) {
        var directive = {
            link: link,
            transclude: true,
            restrict: 'E',
            template: "<div ng-transclude></div>"
        };
        return directive;

        function link(scope, element) {
            var elementTop = element.offset().top;

            $document.on('scroll', detectElementVisibilityChange)
            scope.$on('$destroy', function () {
                $document.off('scroll', detectElementVisibilityChange);
            });

            function detectElementVisibilityChange() {
                var scrollTop = angular.element($window).scrollTop();
                if (scrollTop > elementTop) {
                    element.addClass("floating");
                    element.css('height', element.contents().outerHeight());
                } else {
                    element.removeClass("floating");
                    element.css('height', null);
                }
            }
        }
    }
})();

