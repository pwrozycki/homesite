(function () {
    'use strict';

    angular
        .module('angular')
        .directive('lazyLoaderContainer', lazyLoaderContainer);

    /* @ngInject */
    function lazyLoaderContainer($window, lazyLoaderService, $timeout) {
        var directive = {
            bindToController: true,
            controller: LazyLoaderContainerController,
            controllerAs: 'vm',
            link: link,
            scope: {}
        };
        return directive;

        function link(scope, element) {
            var jqWindow = angular.element($window);

            jqWindow.on('scroll', applyShowComponents);
            jqWindow.on('resize', applyShowComponents);

            element.on('$destroy', function() {
                jqWindow.off('scroll', applyShowComponents);
                jqWindow.off('resize', applyShowComponents);
            });

            $timeout(showComponents);

            function applyShowComponents() {
                scope.$apply(showComponents);
            }

            function showComponents() {
                lazyLoaderService.notifyVisibleComponents(scope.vm.childComponents);
            }
        }
    }

    /* @ngInject */
    function LazyLoaderContainerController() {
        var vm = this;
        vm.childComponents = [];
        vm.addComponent = addComponent;

        function addComponent(childComponent) {
            vm.childComponents.push(childComponent);
        }
    }

})();

