(function () {
    'use strict';

    angular
        .module('angular')
        .directive('fixedWidget', fixedWidget);

    /* @ngInject */
    function fixedWidget($window, $document, _) {
        var directive = {
            link: link,
            transclude: true,
            restrict: 'E',
            template: "<div ng-transclude></div>"
        };
        return directive;

        function link(scope, element) {
            var detectElementVisibilityChangeThrottled = _.throttle(detectElementVisibilityChange, 100);
            var floating = false;

            $document.on('scroll', detectElementVisibilityChangeThrottled);
            scope.$on('$destroy', function () {
                $document.off('scroll', detectElementVisibilityChangeThrottled);
            });

            function detectElementVisibilityChange() {
                var elementTop = element.offset().top;
                var scrollTop = angular.element($window).scrollTop();
                var shouldFloat = scrollTop > elementTop;

                if (shouldFloat && !floating) {
                    floating = true;
                    element.addClass("floating");
                    element.css('height', element.contents().outerHeight());

                } else if (!shouldFloat && floating) {
                    floating = false;
                    element.removeClass("floating");
                    element.css('height', null);
                }
            }
        }
    }
})();

