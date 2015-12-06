(function () {
    'use strict';

    angular
        .module('angular')
        .controller('BrowserController', BrowserController);

    /* @ngInject */
    function BrowserController(directoryPromise, $window, $scope, $timeout, $state, titleService) {
        var vm = this;
        vm.directory = directoryPromise;

        activate();

        ////////////////

        function activate() {
            $scope.$on('$stateChangeSuccess', setScrollPosition);
            $scope.$on('session:logout', leaveBrowserOnLogout);
            $scope.$on('$stateChangeSuccess', invokeLazyLoaderOnBrowserEnter);
            $scope.$watch('browser.directory._images.length', invokeLazyLoaderOnImageListChange);

            titleService.setTitleForState('homeGallery - ' + (vm.directory.path ? vm.directory.path : "ROOT"));
        }

        function invokeLazyLoaderOnImageListChange() {
            invokeLazyLoader();
        }

        function invokeLazyLoaderOnBrowserEnter(event, toState) {
            if (toState.name === 'main.browser') {
                invokeLazyLoader();
            }
        }

        function invokeLazyLoader() {
            $scope.$broadcast('lazyloader:invokeShowComponents');
        }

        function setScrollPosition(event, toState, toParams, fromState, fromParams) {
            if (toState.name === 'main.browser') {
                if (fromState.name === 'main.browser.preview') {
                    $timeout(function () {
                        scrollToImage(fromParams.imageName)
                    });
                } else {
                    angular.element($window).scrollTop(0);
                }
            }
        }

        function leaveBrowserOnLogout() {
            $state.go('main');
        }

        function scrollToImage(imageName) {
            var jqImage = angular.element('img[data-name="' + imageName + '"]');
            if (jqImage.length) {
                var scrollTop = jqImage.offset().top + jqImage.height() / 2 - $window.innerHeight / 2;
                angular.element("body").scrollTop(scrollTop);
            }
        }
    }
})();