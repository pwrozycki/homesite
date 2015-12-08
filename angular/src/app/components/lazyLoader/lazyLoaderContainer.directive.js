(function () {
    'use strict';

    angular
        .module('angular')
        .directive('lazyLoaderContainer', lazyLoaderContainer);

    /* @ngInject */
    function lazyLoaderContainer($window) {
        var directive = {
            bindToController: true,
            controller: LazyLoaderContainerController,
            controllerAs: 'vm',
            link: link,
            scope: {
                visible: '='
            }
        };
        return directive;

        function link(scope, element, attrs, controller) {
            var jqWindow = angular.element($window);

            ['scroll', 'resize'].forEach(function (eventName) {
                jqWindow.on(eventName, controller.showComponents);

                scope.$on('$destroy', function () {
                    jqWindow.off(eventName, controller.showComponents);
                });
            });

            scope.$on('lazyloader:invokeShowComponents', controller.showComponents);
        }
    }

    /* @ngInject */
    function LazyLoaderContainerController(lazyLoaderService, $timeout, _) {
        var vm = this;
        vm.childComponents = [];
        vm.addComponent = addComponent;
        vm.showComponents = _.throttle(showComponents, 100);

        function addComponent(childComponent) {
            var sortedIndex = _.sortedIndex(vm.childComponents, childComponent, "sortingKey");
            vm.childComponents.splice(sortedIndex, 0, childComponent);

            vm.showComponents();
        }

        function showComponents() {
            $timeout(function () {
                lazyLoaderService.notifyVisibleComponents(vm.childComponents);
            });
        }
    }

})();

