(function () {
    'use strict';

    angular
        .module('angular')
        .directive('lazyLoaderComponent', lazyLoaderComponent);

    /* @ngInject */
    function lazyLoaderComponent() {
        var directive = {
            require: '^lazyLoaderContainer',
            link: link,
            restrict: 'E',
            scope: {
                sortingKey: '=',
                show: '&onShow'
            }
        };

        return directive;

        function link(scope, element, attrs, containerCtrl) {
            containerCtrl.addComponent({
                sortingKey: scope.sortingKey,
                element: angular.element(element),
                onShow: scope.show
            });
        }
    }
})();

